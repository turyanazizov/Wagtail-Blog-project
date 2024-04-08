from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail.models import Page, Orderable
from wagtail.snippets.models import register_snippet
from django import forms
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from django.shortcuts import render
from wagtail.models import Page
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from wagtail.documents.models import Document
from django.contrib import messages

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]
    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context

class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    authors = ParentalManyToManyField('blog.Author', blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]
    category = models.ForeignKey(
        'Category', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name="blog_pages"
    )
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('authors', widget=forms.CheckboxSelectMultiple),
            FieldPanel('tags'),
        ], heading="Blog information"),
        FieldPanel('intro'),
        FieldPanel('category'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

@register_snippet
class Author(models.Model):
    name = models.CharField(max_length=255)
    author_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('author_image'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Authors'

@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]

class BlogTagIndexPage(Page):

    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')

        blogpages = BlogPage.objects.filter(tags__name=tag)
        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context

class BlogCategoryIndexPage(Page):

    def get_context(self, request):
        category = request.GET.get('category')
        blogpages = BlogPage.objects.filter(category__name=category)
        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']

class DocumentUploadPage(Page):
    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = DocumentUploadForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Document uploaded successfully!')
                return HttpResponseRedirect(self.url)
            else:
                for error in form.errors:
                    messages.error(request, f"Error uploading document: {form.errors[error]}")
        else:
            form = DocumentUploadForm()

        return render(request, 'document/document_upload_page.html', {
            'page': self,
            'form': form,   
        })


class TechnicalBlogPage(Page):

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogs = BlogPage.objects.filter(category__name='Technical')
        context['blogs'] = blogs
        return context
    
class FoodBlogPage(Page):

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogs = BlogPage.objects.filter(category__name='Food')
        context['blogs'] = blogs
        return context
    
class MarketingBlogPage(Page):

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogs = BlogPage.objects.filter(category__name='Marketing')
        context['blogs'] = blogs
        return context
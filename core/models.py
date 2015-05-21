from django.db import models
from django.contrib.auth.models import User
from thumbs import ImageWithThumbsField
from django.template.defaultfilters import slugify
from froala_editor.fields import FroalaField

# Skills models

class Skills_categories(models.Model):
	title = models.CharField(max_length=128)
	slug = models.SlugField(max_length=100, unique=True)
	description = models.TextField(max_length=500)
	
	def __unicode__(self): 
		return self.title

class Skills(models.Model):
	title = models.CharField(max_length=128)
	category = models.ForeignKey(Skills_categories)
	slug = models.SlugField(max_length=100, unique=True)
	description = models.TextField(max_length=500)
	
	def __unicode__(self): 
		return self.title
	
class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    category = models.ManyToManyField(Skills)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    about = models.TextField(max_length=400)
    date = models.DateField(auto_now_add=True)
    avatar_url = ImageWithThumbsField(upload_to='media/profile_images/thumb', sizes=((700,700),(60,60)))
    

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username
        

# Project model 

class Project(models.Model):
	user = models.ForeignKey(User)
	category = models.ManyToManyField(Skills)
	title = models.CharField(max_length=128)
	date = models.DateField(auto_now_add=True)
	expire_date = models.DateField()
	summary = models.TextField(max_length=400)
	content = FroalaField(options={
        'inlineMode': False, }, theme='troca')
	thumbnail_url = ImageWithThumbsField(upload_to='media/project_images/thumb', sizes=((700,700),(300,300)))
	slug = models.SlugField(max_length=100, unique=True)
	highlighted = models.BooleanField(default=False);
	num_needs = models.IntegerField(default=0)
	
	def __unicode__(self): 
		return self.title
		
class Collaboration(models.Model):
	project = models.ForeignKey(Project)
	date = models.DateField(auto_now_add=True)
	collaborator = models.ForeignKey(User)
	collaboratorSkill = models.ForeignKey(Skills)
	isActive = models.BooleanField(default=False)
	
	def __unicode__(self):
		return unicode("The user: " + str(self.collaborator) + " collaborates in: " + str(self.project.slug) + " with: " + str(self.collaboratorSkill.slug) + "| " + str(self.isActive))

	

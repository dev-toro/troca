# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from core.models import Project, UserProfile, Skills, Skills_categories
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, MultiField, Field, HTML, Column, Div
from django.contrib.auth.forms import AuthenticationForm
from froala_editor.widgets import FroalaEditor


class SkillForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False
    
    title = forms.CharField(
        label = "Nombre de la habilidad",
        required = True,
    )

    description = forms.CharField(
        label = "Descripción",
        required = True,
        max_length = 140,
        widget = forms.Textarea
    )
    
    class Meta:
        model = Skills
        fields = ('title', 'category', 'description')
        
    def __init__(self, *args, **kwargs):
        super(SkillForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
                            
                Fieldset(
                    'Detalles de la habilidad',
                    'title',
                    'description',
                    css_class='large-6 medium-6 columns ml20'
                ),
                Fieldset(
                    'Categoria',
                    'category',
                    css_class='large-5 medium-5 columns'
                ),
                ButtonHolder(Submit('submit', 'Enviar', css_class='button radius ml15')),      
 
            )
    

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    helper = FormHelper()
    helper.form_tag = False
    
    username = forms.CharField(
        label = "apodo | minusculas",
        required = True,
    )
    
    first_name = forms.CharField(
        label = "Nombre",
        required = True,
    )
    
    last_name = forms.CharField(
        label = "Apellido",
        required = True,
    )
    
    email = forms.EmailField(
        label = "Correo electrónico",
        required = True,
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label = "Contraseña",
        required = True,
    )


    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',  'email', 'password')
        
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(

                Fieldset(
                    'Detalles de la cuenta',
                    'username',
                    'first_name', 
                    'last_name',
                    'email',
                    'password',
                    ButtonHolder(Submit('submit', 'Registrarse', css_class='button radius'),  css_class=' text-center'),
                    Div(
                        HTML('<p>Ya eres miembro? <a href="/login/">Inicia sesion</a></p>'),
                        css_class='field-bottom topborder padt15 text-center'
                        ),
                    css_class='large-4 medium-4 medium-centered columns',
                ),
                   
            )

class UserLoginForm(AuthenticationForm):
    password = forms.CharField(widget=forms.PasswordInput())
    helper = FormHelper()
    helper.form_tag = False
    
    username = forms.CharField(
        label = "apodo",
        required = True,
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label = "Contraseña",
        required = True,
    )


    class Meta:
        model = User
        fields = ('username', 'password')
        
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(

                Fieldset(
                    'Detalles de la cuenta',
                    'username',
                    'password',
                    ButtonHolder(Submit('submit', 'Iniciar sesion', css_class='button radius'), css_class=' text-center'),
                    Div(
                        HTML('<p>Eres nuevo en Troca? <a href="/register/">Registrate</a></p>'),
                        css_class='field-bottom topborder padt15 text-center'
                        ),
                    css_class='large-4 medium-4 large-centered medium-centered columns',
                ),
                   
            )

class UserProfileForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False
    
    facebook = forms.CharField(
        label = "Facebook",
        required=False,
    )
    
    twitter = forms.CharField(
        label = "Twitter",
        required=False,
    )
    
    avatar_url = forms.ImageField(
        label = "Imagen del perfil",
        required = True,
    )
       
    category = forms.ModelMultipleChoiceField(
        queryset = Skills.objects.all(), 
        widget = forms.SelectMultiple,
        label = "¿Qué habilidades posee usted?",
        required = True,
    )
    
    about = forms.CharField(
        label = "Cúentanos quíen eres :)",
        required = True,
        max_length = 140,
        widget = forms.Textarea
    )

    class Meta:
        model = UserProfile
        fields = ('category', 'about', 'avatar_url', 'facebook', 'twitter')
        
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
 
            MultiField(
                HTML("<img src='{{ user.userprofile.avatar_url.url_60x60 }}'>"),
                Fieldset(
                    'Opciones generales',
                    'avatar_url',
                    'about',
                    'facebook',
                    'twitter',
                    css_class='large-6 medium-6 columns ml20',
                ),
                Fieldset(
                    'Tengos',
                    'category',
                    HTML("<a  href='/crea/habilidad/' target='_blank'><i class='fa fa-life-ring'></i> Falta alguna habilidad en listado?</a>"),
                    css_class='large-5 medium-5 columns'
                ),
                ButtonHolder(Submit('submit', 'Guardar cambios', css_class='button radius ml15'))
                )
            )
                                    
        
class ProjectForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False
    
    expire_date = forms.DateField(
        label = "Fecha de expiración",
        initial = "Seleccionar una fecha",
        required = True,
    )
    
    title = forms.CharField(
        label = "Título del proyecto",
        required = True,
        max_length = 80,
    )
    
    thumbnail_url = forms.ImageField(
        label = "Imagen principal",
        required = True,
    )
    
    summary = forms.CharField(
        label = "Descripción corta",
        required = True,
        max_length = 140,
        widget = forms.Textarea
    )
    
    content = forms.CharField(
        label = "Contenido",
        required = True,
        widget = FroalaEditor
    )
    
    category = forms.ModelMultipleChoiceField(
        queryset = Skills.objects.all(), 
        widget = forms.SelectMultiple,
        label = "¿Qué habilidades necesita para hacer realidad su proyecto?",
        required = True,
    )
    
    
    class Meta:
        model = Project
        fields = ('title','expire_date','content','category', 'summary', 'thumbnail_url')
        
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
                            
                Fieldset(
                    'Opciones generales',
                    'title',
                    'thumbnail_url',
                    'summary',
                    'content',
                    Field(
                        'expire_date',
                        css_class='datepicker'
                        ),
                    css_class='large-6 medium-6 columns ml20'
                ),
                Fieldset(
                    'Necesidades',
                    'category',
                    HTML("<a  href='/crea/habilidad/' target='_blank'><i class='fa fa-life-ring'></i> Falta alguna habilidad en listado?</a>"),
                    css_class='large-5 medium-5 columns'
                ),
                ButtonHolder(Submit('submit', 'Publicar', css_class='button radius ml15')),      
 
            )

from django.views.generic import View, FormView, UpdateView, CreateView, DetailView, ListView, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from core.forms import UserForm, UserProfileForm, ProjectForm, UserLoginForm, SkillForm
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from registration.signals import user_activated
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache

from django.dispatch import receiver
from django.shortcuts import redirect
from django.http import Http404

from django.template import defaultfilters
from django.template.defaultfilters import slugify
from pure_pagination.mixins import PaginationMixin
from django.contrib.contenttypes.models import ContentType

# Import the models
from django.contrib.auth.models import User
from core.models import Project, Skills_categories, Skills, UserProfile, Collaboration


class AboutView(TemplateView):
    template_name = "foundation/about.html"
    
class OurPeople(TemplateView):
    template_name = "foundation/ourpeople.html"

class Create_skill(CreateView):
    template_name = 'foundation/create_skill.html'
    form_class = SkillForm
    model = Skills
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Create_skill, self).dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        skill = form.save(commit=False)
        skill.slug = defaultfilters.slugify(skill.title)
        skill.save()
        form.save_m2m()
        return HttpResponseRedirect('/')

class Trueques(PaginationMixin,ListView):
    template_name = 'foundation/trueques_view.html'
    model = Collaboration
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super(Trueques, self).get_context_data(**kwargs)
        _collaborator = User.objects.get(username=self.kwargs['username'])
        _UserColab = Collaboration.objects.all().filter(collaborator=_collaborator).exclude(isActive=False)
        
        context['userColabs'] = _UserColab
        
        rev_collaborations = {}
        collaborators_profiles = {}
        donation = {}
        isDonation = False
        _allColab = Collaboration.objects.all()
        index = 0
        
        for c in _allColab: # Recorra todoas las colaboraciones (c) (Collaboration) del usuario loggeado
            cp = Project.objects.get(pk=c.project.pk) # Obtenga los proyectos (cp) de cada colaboracion (c)
            _profile = UserProfile.objects.get(user=c.collaborator) #  Obtena el perfil del usuario que hizo la colaboraciond (c) conmigo (_collaborator)
            #print("usuario loggeado: " + str(_collaborator) + " es igual a? " + str(cp.user))
            if  cp.user == _collaborator and c.isActive: # Si el usuario de ese proyecto (cp) es igual del usuario loggeado (_collaborator) entonces recibi una colaboracion
                #print("hay trueque")
                collaborators_profiles[c.collaborator] = [_profile] # Guarde el perfil
                rev_collaborations[index] = [c] # Guarde la colaboracion (c)
                index += 1
                
        for c in _allColab:
            cp = Project.objects.get(pk=c.project.pk) # coja ese proyectp (cp)
            _profile = UserProfile.objects.get(user=cp.user) #  Obtena el perfil del usuario (_profile) de ese proyecto (cp)
            keysList = list(collaborators_profiles.keys())
            if _collaborator == c.collaborator and _profile.user not in keysList and c.isActive: # revise si el usuario loggeado (_collaborator) tiene alguna / donacion
                #print("hay donacion")
                isDonation = True
                donation[_profile] = [c]
                index += 1            
        
        context['isDonation'] = isDonation
        context['donation'] = donation
        #print("donacion? = " + str(isDonation))
        
        context['revColabs'] = rev_collaborations
        context['colabsProfiles'] = collaborators_profiles
        
        return context
    
    def get_queryset(self):
        qs = super(Trueques, self).get_queryset()
        
        _collaborator = User.objects.get(username=self.kwargs['username'])
        
        rev_collaborations = []
        
        for c in qs:
            cp = Project.objects.get(pk=c.project.pk)
            if  cp.user == _collaborator and c.isActive:
                rev_collaborations.append(c.collaborator)                
        
        _result = list(set(rev_collaborations))
        #print(str(_result))
        
        return _result
    
@login_required    
def Del_trueque(request, username):    
        
    _user = User.objects.get(username=username) # el usuario B
    
    if request.user.is_authenticated(): # Compruebe que el usuario este loggeado
        user = request.user # coja El usuario loggeado (user)
        _UserColab = Collaboration.objects.all().filter(collaborator=user) # obtena todas las colaboracions (_UserColab) del usuario loggeado (user)
        print("logged as: " + str(user) + " compiling for " + str(_user))
        for x in _UserColab: # Recorra todas las colaboraciones (_UserColab)
            if x.project.user == _user: # si el autor del proyecto para cada colaboracion (x) es igual al usuario B (_user)
                #print("Desactive la colab de " + str(user) + " con " + str(_user) + " en el proyecyo " + str(x.project) )
                
                # ----- Calculate % of complatness of the project
                    
                numNeeds = x.project.category.count()    
                x.project.num_needs = (x.project.num_needs)-(100/numNeeds)
                x.project.save()
                
                x.isActive = False
                x.save()
                
        _allColab = Collaboration.objects.all()
        _revColab = []
        
        for x in _allColab: # Recorra todas las colaboraciones (_allColab)
            if x.project.user == user: # si el autor del proyecto para cada colaboracion (x) es igual al usuario loggeado (user)
                #print("Desactive la colab de " + str(x.collaborator) + " con " + str(user) + " en el proyecyo " + str(x.project) )
                
                numNeeds = x.project.category.count()    
                x.project.num_needs = (x.project.num_needs)-(100/numNeeds)
                x.project.save()
                
                x.isActive = False
                x.save()        
                
        s = "/colaboraciones/" + user.username
    return HttpResponseRedirect(s)
     
    

class Home(ListView):
    template_name = 'foundation/index.html'
    model = Project
    
    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['selected'] = Project.objects.all().filter(highlighted=True)
        return context
    
    def get_queryset(self):
        qs = super(Home, self).get_queryset()
        return qs.order_by('-date')[:3]

class Users_view(PaginationMixin,ListView):
    template_name = 'foundation/users_view.html'
    model = UserProfile
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super(Users_view, self).get_context_data(**kwargs)
        return context
    
    def get_queryset(self):
        qs = super(Users_view, self).get_queryset()
        return qs.order_by('-date')
    
class Category_view(PaginationMixin,ListView):
    template_name = 'foundation/category_view.html'
    model = Project
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super(Category_view, self).get_context_data(**kwargs)
        
        _cat = {}
        cat = Skills_categories.objects.all()
        
        for x in cat:
            _subCat = Skills.objects.all().filter(category = x)
            count = 0
            for y in _subCat:
                count = count + Project.objects.all().filter(category = y).count()
            _cat[x] = [count]
        
        context['categories'] = _cat
        
        print(str(_cat))
        
        if self.request.user.is_authenticated():
            user = self.request.user
            
            try: 
                userProfile = UserProfile.objects.get(user=user)
                context['loggedUser'] = userProfile
                context['hasProfile'] = True
            except UserProfile.DoesNotExist:
                context['hasProfile'] = False
                          
        return context
    
    def get_queryset(self):
        qs = super(Category_view, self).get_queryset()
        return qs.order_by('-date')

class Category_view_filter(PaginationMixin, ListView):
    template_name = 'foundation/sub_category_view.html'
    model = Project
    paginate_by = 9
    
    def get_context_data(self, **kwargs):
        context = super(Category_view_filter, self).get_context_data(**kwargs)
        cat = Skills_categories.objects.all().get(slug=self.kwargs['category'])
        
        _cat = {}
        _subCat = Skills.objects.all().filter(category=cat)
        count = 0
        
        for x in _subCat:
            count = Project.objects.all().filter(category = x).count()
            _cat[x] = [count]
        
        context['sub_categories'] = _cat
        context['main_category'] = cat
        
        if self.request.user.is_authenticated():
            user = self.request.user
            try: 
                userProfile = UserProfile.objects.get(user=user)
                context['loggedUser'] = userProfile
                context['hasProfile'] = True
            except UserProfile.DoesNotExist:
                context['hasProfile'] = False
        
        return context
    
    def get_queryset(self):
        qs = super(Category_view_filter, self).get_queryset()
        cat = Skills_categories.objects.all().filter(slug=self.kwargs['category'])
        sub_cat = Skills.objects.all().filter(category=cat)
        return qs.filter(category=sub_cat).distinct()

class Sub_category_view_filter(PaginationMixin, ListView):
    template_name = 'foundation/detail_sub_category.html'
    model = Project
    paginate_by = 9
    
    def get_context_data(self, **kwargs):
        context = super(Sub_category_view_filter, self).get_context_data(**kwargs)
        cat = Skills_categories.objects.all().get(slug=self.kwargs['category'])
        _cat = Skills.objects.all().get(slug=self.kwargs['subcategory'])
        context['main_category'] = cat
        context['subcategory'] = _cat
        
        if self.request.user.is_authenticated():
            user = self.request.user
            try: 
                userProfile = UserProfile.objects.get(user=user)
                context['loggedUser'] = userProfile
                context['hasProfile'] = True
            except UserProfile.DoesNotExist:
                context['hasProfile'] = False
            
        return context
    
    def get_queryset(self):
        qs = super(Sub_category_view_filter, self).get_queryset()
        cat = Skills.objects.all().filter(slug=self.kwargs['subcategory'])
        return qs.filter(category=cat)



class Project_view(DetailView):
    template_name = 'foundation/project.html'
    model = Project
    slug_field = 'slug'
       
    def get_context_data(self, **kwargs):
        context = super(Project_view, self).get_context_data(**kwargs)
        
        author = User.objects.get(username=self.kwargs['username'])
        user_profile = UserProfile.objects.get(user=author.id) 
        project = Project.objects.get(slug=self.kwargs['slug'])
        
        colabs = Collaboration.objects.all().filter(project=project).exclude(isActive=False) # guarde todas las colaboraciones de ese proyecto
        
        context['author'] = user_profile
        context['author_user'] = author
        
        contType = ContentType.objects.get(app_label='core', model='project').id
        context['contType'] = contType
        
        userColab = {}
        supp_needs = []
        needs = []
        
        for x in project.category.all():
            needs.append(x)    
        
        for x in colabs:
            userColab_user = User.objects.get(username=x.collaborator)
            userColab_profile = UserProfile.objects.get(user=userColab_user)
            userColab[x.collaborator] = userColab_profile.avatar_url
            if x.collaboratorSkill in needs and x.isActive:
                supp_needs.append(x.collaboratorSkill)
        
        #print("tutut " + str(supp_needs))
        
        context['colaborations'] = supp_needs # Guarda las necesidades que ya han sido satisfechas
        context['collaborators'] = userColab # Guarda los usuarios de esas colaboracione y su foto
        
        #print(str(userColab))
            
        if self.request.user.is_authenticated():
            user = self.request.user
            
            try: 
                userProfile = UserProfile.objects.get(user=user) 
                context['hasProfile'] = True
                
                userProjects = Project.objects.all().filter(user=user)            
            
                context['loggedUser'] = userProfile
                context['loggedUserProjects'] = userProjects
                
                userGives = {}
                userRecives = {}
                
                context['isReverseMatch'] = False
                context['isMatch'] = False
                match = [] # guarde los match aca (category)        
    
                index = 1
                
                #----------------------> Que puede aportar el usuario logged al proyecto? <----------------
    
                for x in userProfile.category.all(): # Rocorro las habilidades del usuario logeado (x) (category)
                    for y in project.category.all(): # Recorro las necesidades del proyecto (y) (category)    
                        if x.slug == y.slug: # SI la habilidad (x) y la nececidad (y) coinciden                        
                            match.append(x) # con cuales habilidades? guardelas en una lista (x) (category)
                            
                print ("hay match con estas habilidades: " + str(match))
                                                    
                if colabs.exists(): # Si existen colaboraciones
                    
                    print ("existen estas colaboraciones: " + str(colabs))
                    
                    for i in colabs: # Recorro esas colaboraciones
                        for r in match: # Recorro los match / coincidencias /// may prove necesary ----- and i.collaboratorSkill.slug in match
                            if i.collaboratorSkill.slug != r.slug and i.project == project and i.isActive: # Y la habilidad de esa colaboracion (i) es diferente a las habilidades (match) del usuario (x) 
                                context['isMatch'] = True # Hay una posibilidad de intercambio
                                s = "Alternativa " + str(index)
                                userGives[s] = [r.slug]
                                index += 1
                                                            
                else: # No existen colaboraciones ---> entonces muestreme todas los (match) coincidencias
                    for r in match:
                        context['isMatch'] = True # Hay una posibilidad de intercambio
                        s = "Alternativa " + str(index)
                        userGives[s] = [r.slug]
                        index += 1
                        
                #----------------------> Que puede aportar el autor del proyecto al usuario logged? <----------------
                
                rev_match = [] # guarde los match aca (category)
                rev_colabs = [] # guarde las colaboraciones        
                            
                for x in user_profile.category.all(): # Recorro las habilidaes del autor del proyecto (x)
                    for y in userProjects.all(): # Recorro los proyectos del usuario loggeado (y)    
                        for yy in y.category.all():    # Colecto las necesidades de todos los proyectos del usuario loggeado (yy)    
                            if x.slug == yy.slug: # coinciden?
                                context['isReverseMatch'] = True # You can give and recive
                                rev_match.append(x)
                                colabs = Collaboration.objects.all().filter(project=y)
                                                
                                if colabs.exists():
                                                    
                                    for i in colabs:
                                        if i.collaboratorSkill.slug != x.slug and i.isActive:
                                            _reciverProject = y
                                            userRecives[_reciverProject.title] = [yy.slug]
                                                            
                                        elif i.isActive == False:
                                            _reciverProject = y
                                            userRecives[_reciverProject.title] = [yy.slug]
                                else:
                                    _reciverProject = y
                                    userRecives[_reciverProject.title] = [yy.slug]
                                                            
                    #print("Log puede dar: " + str(userGives) + " y puede recivir: " + str(userRecives))
            
                context['userRecives'] = userRecives
                context['userGives'] = userGives
                
            except UserProfile.DoesNotExist:
                context['hasProfile'] = False
            
        

        return context
    
@login_required
def register_collaborator(request, username, slug):
    
    
    project_base = Project.objects.get(slug=slug)
    loggedUser = User.objects.get(username=username) 
    skill_given_loggedUser = Skills.objects.get(slug=request.POST['gives'])
    project_author = User.objects.get(username=project_base.user)
    
    # ---- Register collaborator in base project
            
    new_collab = Collaboration(project=project_base, collaborator=loggedUser, collaboratorSkill=skill_given_loggedUser, isActive = True);
    new_collab.save()
        
    # ----- Calculate % of complatness of the project
    numNeeds = project_base.category.count()    
    project_base.num_needs = (project_base.num_needs)+(100/numNeeds)
    project_base.save()
        
        # ---- Register collaborator in logged user project
    req = request.POST.get('receives', False)
    
    if req:
    
        a, b = req.split("/")
        
        project_loggedUser = Project.objects.get(title=a)
        skill_recived_loggedUser = Skills.objects.get(slug=b)
            
        _new_collab = Collaboration(project=project_loggedUser, collaborator=project_author, collaboratorSkill=skill_recived_loggedUser, isActive = True);
        _new_collab.save()
        
            # ----- Calculate % of complatness of the project
        _numNeeds = project_loggedUser.category.count()    
        project_loggedUser.num_needs = (project_loggedUser.num_needs)+(100/_numNeeds)
        project_loggedUser.save()
        
    
    #print("Usuario " + username + " Quiere colaborar en " + slug + " prestando el servicio de " + request.POST['gives'] + " y recibiendo " + b + " in the project " + a)
        
    s = "/colaboraciones/" + loggedUser.username
    return HttpResponseRedirect(s)

class Profile(PaginationMixin, DetailView):
    template_name = 'foundation/user_profile.html'
    model = UserProfile
    slug_field = 'user'
    paginate_by = 3
    
    def get_context_data(self, **kwargs):
        context = super(Profile, self).get_context_data(**kwargs)
        _user = User.objects.get(id=self.kwargs['slug'])
        user_projects = Project.objects.all().filter(user=_user)
        context['hasProjects'] = user_projects.exists()
        context['projects'] = user_projects
        
        contType = ContentType.objects.get(app_label='core', model='userprofile').id
        context['contType'] = contType

        return context
    
    def get_queryset(self):
        qs = super(Profile, self).get_queryset()
        return qs.order_by('-date')
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            # redirect here
            return redirect('/register/perfil/')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/')

class Create_profile(CreateView):
    template_name = 'registration/create_profile.html'
    form_class = UserProfileForm
    model = UserProfile
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Create_profile, self).dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        user_profile = form.save(commit=False)
        user_profile.user = self.request.user
        user_profile.save()
        form.save_m2m()
        return HttpResponseRedirect('/')
 
class Settings(UpdateView):
    template_name = 'foundation/settings.html'
    form_class = UserProfileForm
    model = UserProfile
    state = False
    
    def get_state(self):
        return state
    
    def get_object(self, queryset=None):
        user = User.objects.get(username=self.kwargs['username'])
        obj = UserProfile.objects.get(user=user.id)
        return obj
    
    def form_valid(self, form):
        userProfile = form.save()
        s = "/perfil/"
        s = s + str(userProfile.user.id);
        return HttpResponseRedirect(s)

class Edit_project(UpdateView):
    template_name = 'foundation/edit_project.html'
    form_class = ProjectForm
    model = Project
    
    def form_valid(self, form):
        project = form.save()
        s = "/proyecto/"
        s = s + project.user.username + "/" + project.slug;
        return HttpResponseRedirect(s)

class Create_project(CreateView):
    template_name = 'foundation/create.html'
    form_class = ProjectForm
    model = Project
    
    def form_valid(self, form):
        project = form.save(commit=False)
        project.user = self.request.user
        project.slug = defaultfilters.slugify(project.title)
        project.save()
        form.save_m2m()
        s = "/proyecto/"
        s = s + project.user.username + "/" + project.slug;
        return HttpResponseRedirect(s)

@receiver(user_activated)
def login_on_activation(sender, user, request, **kwargs):
    """Logs in the user after activation"""
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    #auth_login(request, user)
 
# Registers the function with the django-registration user_activated signal
user_activated.connect(login_on_activation) 
    

class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = UserForm
    model = User
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = user.username.lower()
        user.set_password(user.password)
        user.save()
        user_activated.send(sender=self, user=user, request=self.request)
        return HttpResponseRedirect('/register/perfil/')
    
class Login(FormView):
    template_name = 'registration/login.html'
    form_class = UserLoginForm
    success_url = '/'

    redirect_field_name = REDIRECT_FIELD_NAME
    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()
        return super(Login, self).dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            
        return super(Login, self).form_valid(form)
    
    def get_success_url(self):
        redirect_to = self.request.REQUEST.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to
        

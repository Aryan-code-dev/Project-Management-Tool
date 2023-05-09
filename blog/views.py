from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import *
from django.views.generic import ListView,DetailView, CreateView,UpdateView, DeleteView
# from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# Create your views here.
from accounts.models import *
curr_user = ''
def home(request): 
    context = {
        'posts' : Post.objects.all()
    }
    curr_user = request.session['user_id']
    return render(request, 'blog/home.html',context)
    # return HttpResponse('<h1>Welcome TO NewsDaily</h1>')

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_post.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5


    def get_queryset(self):
        user = get_object_or_404(User, username = self.kwargs.get('username'))
        return Post.objects.filter(author = user).order_by('-date_posted')

class PostDetailView(DetailView):
    model = Post

def postdetail(request,pk):
    print("done with it")
    print(pk)
    obj = get_object_or_404(Post,id = pk)
    print(obj.author)
    context = {
        'comments' : comment.objects.filter(post_id = pk),
        'object' : obj,
    }
    # curr_user = request.session['user_id']
    return render(request, 'blog/post_detail.html',context)

class PostCreateView(LoginRequiredMixin,CreateView):
    model = Post
    fields = ['title','content']

    def form_valid(self, form):
        form.instance.author = self.request.user    
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    print("hello")
    model = Post
    fields = ['title','content']

    def form_valid(self, form):
        form.instance.author = self.request.user    
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin,DeleteView):
    model = Post

    success_url = '/'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    # return HttpResponse('Hello noobs')
    return render(request, 'blog/about.html',{'title' : 'About'})

def post_comment(request,pk):
        print("HEllo")
        con = request.POST.get('user_comment')
        author = request.user
        post_id = get_object_or_404(Post,id = pk)
        post_author = (request.POST['my_field'])
        print(con,author,post_id,post_author)
        comm = comment(author = author,content= con,post_id=post_id)

        # comment = comment(author = author,content = content,post_id = post_id)

        comm.save()
        obj = get_object_or_404(Post,id = pk)

        context = {
            'comments' : comment.objects.filter(post_id = pk),
            'object' : obj,
        }

        # return redirect ('blog:post_detail',context = context)
        return render(request, 'blog/post_detail.html',context)
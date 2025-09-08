from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone
from django.http import HttpResponseForbidden, Http404

from .models import Category, Post, Comment
from .forms import PostForm, CommentForm, UserUpdateForm
from .services import filter_posts_by_publication

User = get_user_model()


def index(request):
    post_list = filter_posts_by_publication().annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if not post.is_published and post.author != request.user:
        raise Http404("Post not found")

    if (
        post.category and not post.category.is_published
        and post.author != request.user
    ):
        raise Http404("Post not found")

    if (
        post.pub_date > timezone.now()
        and post.author != request.user
    ):
        raise Http404("Post not found")

    form = CommentForm()
    comments = post.comments.select_related('author')
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': form,
        'comments': comments
    })


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = filter_posts_by_publication(category.posts.all()).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj}
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.select_related('category', 'location').annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    if request.user != profile_user:
        posts = filter_posts_by_publication(posts)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/profile.html', {
        'profile': profile_user,
        'page_obj': page_obj
    })


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.is_published = True
            try:
                post.save()
                form.save_m2m()
                return redirect('blog:profile', username=request.user.username)
            except Exception as e:
                print(f"Error saving post: {e}")
        else:
            print(f"Post form errors: {form.errors}")
    else:
        form = PostForm()

    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    return render(
        request, 'blog/create.html',
        {'form': PostForm(instance=post)}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', post_id=post_id)
        else:
            print(f"Comment form errors: {form.errors}")
    else:
        form = CommentForm()

    comments = post.comments.select_related('author')
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': form,
        'comments': comments
    })


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'comment': comment
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            try:
                user = form.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                return redirect('blog:profile', username=request.user.username)
            except Exception as e:
                print(f"Error saving profile: {e}")
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})

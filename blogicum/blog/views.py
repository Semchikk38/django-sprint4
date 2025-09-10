from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import Http404

from .models import Category, Post, Comment
from .forms import PostForm, CommentForm, UserUpdateForm
from .services import get_published_posts, paginate_posts

User = get_user_model()


def index(request):
    post_list = get_published_posts()
    page_obj = paginate_posts(request, post_list)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        if post.author != request.user:
            post = get_object_or_404(
                get_published_posts(),
                id=post_id
            )
    else:
        post = get_object_or_404(
            get_published_posts(),
            id=post_id
        )

    form = CommentForm(request.POST or None)
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
    post_list = get_published_posts().filter(category=category)
    page_obj = paginate_posts(request, post_list)

    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj}
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        posts = profile_user.posts.select_related('category', 'location')
    else:
        posts = get_published_posts().filter(author=profile_user)

    page_obj = paginate_posts(request, posts)

    return render(request, 'blog/profile.html', {
        'profile': profile_user,
        'page_obj': page_obj
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.is_published = True
        post.save()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

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
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)

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
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'comment': comment
    })


@login_required
def profile_edit(request):
    form = UserUpdateForm(request.POST or None, instance=request.user)

    if form.is_valid():
        user = form.save()
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/user.html', {'form': form})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Reply
from .forms import PostForm, ReplyForm
from django.http import Http404


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community_feed')
    else:
        form = PostForm()
    
    return render(request, 'community/community_feed.html', {'form': form})

@login_required
def create_reply(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.save()
            return redirect('community_feed')
    return redirect('community_feed')

# View for Deleting a Post
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:
        post.delete()
    return redirect('community_feed') 


@login_required
def community_feed(request):
    posts = Post.objects.all().order_by('-created_at')
    replies = Reply.objects.all().order_by('created_at')

    post_form = PostForm()
    reply_form = ReplyForm()

    if request.method == "POST":
        # Creating a new post
        if "create_post" in request.POST:
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.user = request.user
                post.save()
                return redirect("community_feed")  # Refresh the page to show the new post

        # Replying to a post or reply
        elif "content" in request.POST:
            content = request.POST.get("content")
            post_id = request.POST.get("post_id")
            parent_id = request.POST.get("parent_id")

            if content:
                if parent_id:  # Replying to a reply
                    parent_reply = get_object_or_404(Reply, id=parent_id)
                    Reply.objects.create(
                        user=request.user,
                        post=parent_reply.post,  # Get the original post from the parent reply
                        content=content,
                        parent=parent_reply
                    )
                elif post_id:  # Replying to a post
                    post = get_object_or_404(Post, id=post_id)
                    Reply.objects.create(
                        user=request.user,
                        post=post,
                        content=content
                    )

                return redirect("community_feed")  # Refresh the page to show the new reply

        # Deleting a post
        elif "delete_post_id" in request.POST:
            post_to_delete = get_object_or_404(Post, id=request.POST.get("delete_post_id"), user=request.user)
            post_to_delete.delete()
            return redirect("community_feed")

        # Deleting a reply
        elif "delete_reply_id" in request.POST:
            reply_to_delete = get_object_or_404(Reply, id=request.POST.get("delete_reply_id"), user=request.user)
            reply_to_delete.delete()
            return redirect("community_feed")

    return render(request, "community/community_feed.html", {
        "posts": posts,
        "replies": replies,
        "post_form": post_form,
        "reply_form": reply_form
    })

@login_required
def reply_to_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Reply.objects.create(user=request.user, post=post, content=content)
            return redirect("community_feed")

    # Render the reply form when accessed via GET request
    return render(request, "community/reply_to_post.html", {"post": post})



@login_required
def reply_to_reply(request, reply_id):
    parent_reply = get_object_or_404(Reply, id=reply_id)
    post = parent_reply.post  # Get the associated post
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Reply.objects.create(
                user=request.user,
                post=post,
                content=content,
                parent=parent_reply  # This reply is a reply to another reply
            )
            return redirect('community_feed')  # Redirect to community feed

    return render(request, 'community/reply_to_reply.html', {'parent_reply': parent_reply})
@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)

    if reply.user == request.user:  # Only allow the owner to delete their reply
        reply.delete()

    return redirect('community_feed')

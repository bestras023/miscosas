import os

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render, redirect

from accounts.models import Profile
from miscosas.settings import BASE_DIR
from .parser import *
from .models import *


def home(request):
    if 'style' not in request.session:
        request.session['style'] = 'light'
    if 'font_size' not in request.session:
        request.session['font_size'] = '1rem'
    template_name = 'home/home.html'
    if request.is_ajax():
        flag = request.POST['flag']
        if flag == 'get_10_items':
            # get 10 items with the most score
            items_10 = 'empty'
            if Item.objects.count() != 0:
                items_10 = Item.objects.all()[:10].values('id', 'title', 'link', 'score', 'positive_score', 'negative_score')
                items_10 = list(items_10)
            return JsonResponse({"items_10": items_10})
        elif flag == 'get_feeders':
            feeder_values = 'empty'
            if Feeder.objects.filter(visible_status=True).count() != 0:
                feeder_values = Feeder.objects.filter(visible_status=True).values(
                    'id', 'title', 'link', 'item_number', 'score')
                feeder_values = list(feeder_values)
            return JsonResponse({"feeder_values": feeder_values})
        elif flag == 'create_feeder':
            feeder_name = request.POST['feeder']
            url = request.POST['url']
            if Feeder.objects.filter(link__iendswith=url).count() == 1:
                result = "exist"
                return JsonResponse({"result": result})
            result = ""
            if feeder_name == "Youtube":
                url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + url
                result = youtube_parser(url)
            elif feeder_name == "Reddit":
                url = "https://www.reddit.com/r/" + url + ".rss"
                result = subreddit_parser(url)
            return JsonResponse({"result": result})
        elif flag == 'hide_feeder':
            feeder_id = request.POST['feeder_id']
            Feeder.objects.filter(id=feeder_id).update(visible_status=False)
            return JsonResponse({"result": "hide"})
        elif flag == 'show_feeder':
            feeder_id = request.POST['feeder_id']
            Feeder.objects.filter(id=feeder_id).update(visible_status=True)
            return JsonResponse({"result": "show"})
    context = {
        "current_menu": "home"
    }
    return render(request, template_name, context)


def home_xml(request):
    xml_path = os.path.join(BASE_DIR, 'home', 'templates', 'home', 'home.xml')
    items_10 = Item.objects.all()[:10]
    feeder_list = Feeder.objects.filter(visible_status=True)
    response = render(None, xml_path, {"items": items_10, "feeders": feeder_list})
    response['Content-Type'] = 'application/xml'
    return response


def items(request):
    template_name = 'home/items.html'
    item_list = Item.objects.all()
    context = {
        "current_menu": "items",
        "item_list": item_list
    }
    return render(request, template_name, context)


def handle_score(kind, updated_score, updated_positive_score, updated_negative_score):
    if kind == 'positive':
        updated_score += 1
        updated_positive_score += 1
    elif kind == 'negative':
        updated_score -= 1
        updated_negative_score += 1
    return updated_score, updated_positive_score, updated_negative_score


def item(request, item_id):
    template_name = 'home/item.html'
    if not Item.objects.filter(id=item_id).exists():
        return redirect('home:items')
    selected_item = Item.objects.filter(id=item_id)
    selected_item_first = selected_item.first()
    comments = Comment.objects.filter(commented_item=selected_item_first)
    context = {
        "current_menu": "items" + " : " + selected_item_first.title,
        "selected_item": selected_item_first,
        "comments": comments
    }
    if 'id' in request.session:
        # check voted status
        voted_status = False
        user_id = request.session['id']
        current_user = User.objects.get(id=user_id)
        profile = Profile.objects.filter(user=current_user)
        profile_first = profile.first()
        voted_item_ids = profile_first.voted_item_ids.split(",")
        voted_item_ids = list(filter(None, voted_item_ids))
        if str(item_id) in voted_item_ids:
            voted_status = True
        # check comment status
        commented_status = False
        if Comment.objects.filter(creator=current_user, commented_item=selected_item_first).exists():
            commented_status = True
        context['voted_status'] = voted_status
        context['commented_status'] = commented_status
        if request.is_ajax():
            flag = request.POST['flag']
            if flag == 'vote':
                kind = request.POST['kind']
                # update Profile table
                voted_item_ids.append(item_id)
                updated_voted_item_ids = ",".join(voted_item_ids)
                profile.update(voted_item_ids=updated_voted_item_ids)
                # update Item table
                updated_score = selected_item_first.score
                updated_positive_score = selected_item_first.positive_score
                updated_negative_score = selected_item_first.negative_score
                result = handle_score(kind, updated_score, updated_positive_score, updated_negative_score)
                selected_item.update(
                    score=result[0], positive_score=result[1], negative_score=result[2]
                )
                # update Feeder table
                updated_feeder = selected_item_first.feed
                selected_feeder = Feeder.objects.filter(id=updated_feeder.id)
                updated_feeder_score = updated_feeder.score
                updated_feeder_positive_score = updated_feeder.positive_score
                updated_feeder_negative_score = updated_feeder.negative_score
                result = handle_score(kind, updated_feeder_score, updated_feeder_positive_score,
                                      updated_feeder_negative_score)
                selected_feeder.update(
                    score=result[0], positive_score=result[1], negative_score=result[2]
                )
                return JsonResponse({"result": "ok"})
            elif flag == 'comment':
                text = request.POST['text']
                Comment.objects.create(
                    creator=current_user, commented_item=selected_item_first, description=text
                )
                return JsonResponse({"result": "ok"})
    return render(request, template_name, context)


def feeders(request):
    template_name = 'home/feeders.html'
    feeder_list = Feeder.objects.all()
    context = {
        "current_menu": "feeders",
        "feeder_list": feeder_list
    }
    return render(request, template_name, context)


def feeder(request, feeder_id):
    template_name = 'home/feeder.html'
    feed = Feeder.objects.filter(id=feeder_id).first()
    item_feed = Item.objects.filter(feed=feed)
    context = {
        "current_menu": "feeders" + " : " + feed.title,
        "feed_id": feed.id,
        "feed_title": feed.title,
        "feed_link": feed.link,
        "number_of_items": len(item_feed),
        "feed_visible_status": feed.visible_status,
        "item_feed": item_feed
    }
    return render(request, template_name, context)


def users(request):
    if 'id' not in request.session:
        return redirect('home:home')
    template_name = 'home/users.html'
    profiles = Profile.objects.all()
    profile_list = []
    for profile in profiles:
        user_id = profile.user.id
        username = profile.user.username
        photo = profile.photo
        voted_item_number = profile.voted_item_ids.split(",")
        voted_item_number = list(filter(None, voted_item_number))
        voted_item_number = len(voted_item_number)
        one = {
            'user_id': user_id, 'username': username, 'photo': photo, 'voted_item_number': voted_item_number
        }
        profile_list.append(one)
    context = {
        "current_menu": 'users',
        'profile_list': profile_list
    }
    return render(request, template_name, context)


def user(request, user_id):
    if 'id' not in request.session:
        return redirect('home:home')
    template_name = 'home/user.html'
    current_user = User.objects.get(id=user_id)
    profile = Profile.objects.filter(user=current_user)
    # get list of voted items
    voted_item_ids = profile.first().voted_item_ids.split(",")
    voted_item_ids = list(filter(None, voted_item_ids))
    voted_items = Item.objects.filter(id__in=voted_item_ids)
    # get list of commented items
    commented_items = Comment.objects.filter(creator=current_user)
    context = {
        "user_id": user_id,
        "current_menu": 'users',
        "current_user": current_user,
        "voted_items": voted_items,
        "commented_items": commented_items
    }
    if request.method == 'POST':
        file = request.FILES
        if 'photo' in file:
            if request.session['photo_url'] != 'images/default.png':
                past_photo = str(profile.first().photo)
                remove_photo_path = os.path.join(BASE_DIR, 'media', past_photo)
                os.remove(remove_photo_path)
            file = file['photo']
            fs = FileSystemStorage()
            fs.save(file.name, file)
            profile.update(photo=file)
            photo_url = Profile.objects.get(user=current_user).photo.url
            request.session['photo_url'] = photo_url
            return render(request, template_name, context)
    if request.is_ajax():
        flag = request.POST['flag']
        if flag == 'style':
            if request.session['style'] == 'dark':
                request.session['style'] = 'light'
            else:
                request.session['style'] = 'dark'
        elif flag == 'font_size':
            font_size = request.POST['font_size']
            request.session['font_size'] = font_size
        return JsonResponse({"result": "ok"})
    return render(request, template_name, context)


def info(request):
    template_name = 'home/information.html'
    context = {
        "current_menu": "information"
    }
    return render(request, template_name, context)

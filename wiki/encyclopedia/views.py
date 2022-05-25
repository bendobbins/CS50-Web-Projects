import random
from django.http import HttpResponseRedirect
from django.shortcuts import render
import markdown2

from . import util

def index(request):
    if request.method == "POST":
        search = request.POST.get('q').lower()
        substrings = []
        for entry in util.list_entries():
            if search == entry.lower():
                return HttpResponseRedirect(f"wiki/{search}")
            if search in entry.lower():
                substrings.append(entry)
        request.session["current_page"] = "index"
        return render(request, "encyclopedia/index.html", {
            "header": "Pages you might be looking for:",
            "entries": substrings
        })
    request.session["current_page"] = "index"
    return render(request, "encyclopedia/index.html", {
        "header": "All Pages",
        "entries": util.list_entries()
    })


def wiki_page(request, entry):
    page = util.get_entry(entry)
    if page:
        pageHTML = markdown2.markdown(page)
        request.session["current_page"] = entry
        return render(request, "encyclopedia/entry.html", {
            "title": entry.capitalize(),
            "page": pageHTML,
            "valid": True
        })
    request.session["current_page"] = "error"
    return render(request, "encyclopedia/entry.html", {
        "title": "Page Not Found",
        "page": "<h1>Error</h1> <h5>Could not find an entry for that topic</h5>"
    })


def rand(request):
    return HttpResponseRedirect(f"wiki/{random.choice(util.list_entries())}")


def create(request):
    request.session["current_page"] = "create"
    return render(request, "encyclopedia/editor.html", {
        "title": "Create a Page",
        "create": True,
    })


def edit(request):
    page = request.session["current_page"]
    textToEdit = util.get_entry(page)
    return render(request, "encyclopedia/editor.html", {
        "title": f"Editing {page}",
        "create": False,
        "existing": textToEdit
    })


def save(request):
    title = request.POST.get("title")
    body = request.POST.get("body")
    
    if title:
        for entry in util.list_entries():
            if title.lower() == entry.lower():
                return render(request, "encyclopedia/entry.html", {
                    "title": "Saving Error",
                    "page": "<h1>A page with that title already exists.</h1> <h3>Only create pages that do not yet exist."
                })
    else:
        title = request.session["current_page"]

    util.save_entry(title, body)
    return HttpResponseRedirect(f"wiki/{title}")
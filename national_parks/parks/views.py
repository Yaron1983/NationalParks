from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from .models import Park, Rating
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .forms import ParkForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseForbidden
import requests
from dotenv import load_dotenv
import os
load_dotenv()

class HomeView(ListView):
    model = Park
    template_name = 'home.html'
    context_object_name = 'parks'


    def get(self, request, *args, **kwargs):
        print("HomeView GET called")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q")
        country = self.request.GET.get("country")

        if q:
            queryset = queryset.filter(name__icontains=q)
        if country:
            queryset = queryset.filter(country=country)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = (
            Park.objects.exclude(country__isnull=True)
                        .exclude(country__exact="")
                        .values_list("country", flat=True)
                        .distinct()
                        .order_by("country")
        )
        return context

class ParkCreateView(UserPassesTestMixin, CreateView):
    model = Park
    form_class = ParkForm
    template_name = 'parks/park_form.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return HttpResponseForbidden("you don't have permission to add parks")

class ParkListView(ListView):
    model = Park
    template_name = 'parks/park_list.html'
    context_object_name = 'parks'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        sort = self.request.GET.get('sort')
        if sort == 'rating':
            qs = qs.annotate(avg_rating=Avg('ratings__score')).order_by('-avg_rating')
        elif sort == 'name':
            qs = qs.order_by('name')
        return qs

class ParkDetailView(DetailView):
    model = Park
    template_name = 'parks/park_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ratings = self.object.ratings.all().order_by('-created_at')
        if ratings.exists():
            context['average_rating'] = round(sum(r.score for r in ratings) / ratings.count(), 2)
        else:
            context['average_rating'] = None
        context['ratings'] = ratings
        return context

def trip_planner(request, park_id):
    park = get_object_or_404(Park, id=park_id)
    plan = None

    if request.method == "POST":
        user_input = request.POST.get("user_input", "").strip()
        request_type = detect_request_type(user_input)
        if request_type == "general":
            prompt_text = f"""
            You are a professional travel planner.
            Create a short, clear, family-friendly trip plan for **{park.name}**, in **{park.country}**.
            Park info: {park.description or "No description"}.
            Focus on main highlights, attractions, and useful tips.
            Extra info from user: {user_input or "N/A"}.
            """
        else:
            topic = request_type.split(":")[1]
            prompt_text = f"""
            You are a professional travel assistant.
            The user wants **only {topic}** information for **{park.name}** in **{park.country}**.
            Park info: {park.description or "No description"}.
            Respond with concise, accurate info about {topic} relevant to this park and surroundings.
            Extra info from user: {user_input}.
            """

        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are a helpful travel planner."},
                {"role": "user", "content": prompt_text},
            ],
            "temperature": 0.7,
            "max_tokens": 300,
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            plan = data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            plan = f"Error generating trip plan: {str(e)}"

    return render(request, "parks/trip_planner.html", {"park": park, "plan": plan})

def detect_request_type(user_input: str) -> str:
    if not user_input or len(user_input.strip()) == 0:
        return "general"

    text = user_input.lower()

    topics = {
        "hotels": ["hotel", "hotels", "accommodation", "lodging", "hostel", "airbnb", "inn"],
        "restaurants": ["restaurant", "food", "dining", "eat"],
        "hikes": ["hike", "trail", "walk", "trek"],
        "camping": ["camp", "camping", "tent"],
        "transport": ["bus", "car", "train", "transport"],
    }

    for topic, keywords in topics.items():
        if any(word in text for word in keywords):
            return f"specific:{topic}"

    return "general"


@login_required
def rate_park(request, pk):
    park = get_object_or_404(Park, pk=pk)
    score_str = request.POST.get('score')
    try:
        score = int(score_str)
    except (TypeError, ValueError):
        return redirect('park_detail', pk=pk)
    if score < 1 or score > 5:
        return redirect('park_detail', pk=pk)
    comment = (request.POST.get('comment') or '').strip()
    rating, created = Rating.objects.update_or_create(
        user=request.user,
        park=park,
        defaults={'score': score, 'comment': comment}
    )
    return redirect('park_detail', pk=pk)

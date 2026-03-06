from django.shortcuts import render
from .models import ScamType 

def home(request):
    scams = ScamType.objects.all() 
    return render(request, 'ar/index.html', {'scams': scams})

def about(request):
    return render(request, 'ar/about.html')

def report(request):
    return render(request, 'ar/report.html')

def scams(request):
    scams = ScamType.objects.all() 
    return render(request, 'ar/scams.html', {'scams': scams})

def home_en(request):
    scams = ScamType.objects.all() 
    return render(request, 'en/index.html', {'scams': scams})

def about_en(request):
    return render(request, 'en/about.html')

def report_en(request):
    return render(request, 'en/report.html')

def scams_en(request):
    scams = ScamType.objects.all() 
    return render(request, 'en/scams.html', {'scams': scams})

def scam_detail_en(request, pk):
    scam = get_object_or_404(ScamType, pk=pk)
    return render(request, 'en/scam_detail.html', {'scam': scam})

from django.shortcuts import get_object_or_404

def scam_detail(request, pk):
 
    scam = get_object_or_404(ScamType, pk=pk)
    return render(request, 'ar/scam_detail.html', {'scam': scam})

import random
from .models import PhishingScenario

def simulator_view(request):
    all_scenarios = list(PhishingScenario.objects.all())

    sample_size = min(len(all_scenarios), 10)
    random_scenarios = random.sample(all_scenarios, sample_size)
    

    if '/ar/' in request.path:
        return render(request, 'ar/simulator.html', {'scenarios': random_scenarios})
    else:
        return render(request, 'en/simulator.html', {'scenarios': random_scenarios})
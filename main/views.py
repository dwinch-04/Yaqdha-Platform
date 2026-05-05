import random
import json
from collections import defaultdict

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from .models import ScamType, PhishingScenario, UserAttempt, UserProfile, ScenarioReport, SiteWarning, POINTS_MAP, LEVEL_THRESHOLDS


# ─── helpers ────────────────────────────────────────────────────────────────

def _lang(request):
    return 'en' if request.path.startswith('/en/') else 'ar'


def _get_adaptive_scenarios(user, count=10):
    recent = UserAttempt.objects.filter(user=user).select_related('scenario')[:30]

    accuracy = defaultdict(lambda: {'correct': 0, 'total': 0})
    for attempt in recent:
        d = attempt.scenario.difficulty
        accuracy[d]['total'] += 1
        if attempt.was_correct:
            accuracy[d]['correct'] += 1

    # weight: more exposure to difficulties user struggles with
    weights = {'easy': 2, 'medium': 3, 'hard': 2}
    for diff, stats in accuracy.items():
        if stats['total'] > 0:
            rate = stats['correct'] / stats['total']
            if rate > 0.75:
                weights[diff] = 1
            elif rate < 0.50:
                weights[diff] = 5

    all_scenarios = list(PhishingScenario.objects.all())
    pool = []
    for s in all_scenarios:
        pool.extend([s] * weights.get(s.difficulty, 2))

    random.shuffle(pool)
    selected, seen = [], set()
    for s in pool:
        if s.id not in seen:
            selected.append(s)
            seen.add(s.id)
        if len(selected) >= count:
            break

    return selected


# ─── auth ───────────────────────────────────────────────────────────────────

def register_view(request):
    lang = _lang(request)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []
        if not username:
            errors.append('اسم المستخدم مطلوب' if lang == 'ar' else 'Username is required')
        elif User.objects.filter(username=username).exists():
            errors.append('اسم المستخدم مستخدم بالفعل' if lang == 'ar' else 'Username already taken')

        if password1 != password2:
            errors.append('كلمتا المرور غير متطابقتين' if lang == 'ar' else 'Passwords do not match')
        elif len(password1) < 8:
            errors.append('كلمة المرور 8 أحرف على الأقل' if lang == 'ar' else 'Password must be at least 8 characters')

        if not errors:
            user = User.objects.create_user(username=username, password=password1)
            login(request, user)
            return redirect('home' if lang == 'ar' else 'home_en')

        tpl = 'ar/register.html' if lang == 'ar' else 'en/register.html'
        return render(request, tpl, {'errors': errors, 'username': username})

    tpl = 'ar/register.html' if lang == 'ar' else 'en/register.html'
    return render(request, tpl)


def axes_lockout_response(request, credentials, *args, **kwargs):
    lang = _lang(request)
    error = (
        'تم تجميد حسابك مؤقتاً بسبب 5 محاولات فاشلة. حاول مجدداً بعد 30 دقيقة.'
        if lang == 'ar' else
        'Your account is temporarily locked after 5 failed attempts. Try again in 30 minutes.'
    )
    tpl = 'ar/login.html' if lang == 'ar' else 'en/login.html'
    return render(request, tpl, {
        'error': error,
        'locked': True,
        'username': credentials.get('username', ''),
    })


def login_view(request):
    lang = _lang(request)
    tpl = 'ar/login.html' if lang == 'ar' else 'en/login.html'

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home' if lang == 'ar' else 'home_en')

        error = 'اسم المستخدم أو كلمة المرور غير صحيحة' if lang == 'ar' else 'Invalid username or password'
        return render(request, tpl, {'error': error, 'username': username})

    return render(request, tpl)


def logout_view(request):
    lang = _lang(request)
    logout(request)
    return redirect('home' if lang == 'ar' else 'home_en')


# ─── submit answer (AJAX) ────────────────────────────────────────────────────

@require_POST
def submit_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'guest': True})

    try:
        data = json.loads(request.body)
        scenario_id = data['scenario_id']
        was_correct = bool(data['was_correct'])
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({'ok': False}, status=400)

    try:
        scenario = PhishingScenario.objects.get(pk=scenario_id)
    except PhishingScenario.DoesNotExist:
        return JsonResponse({'ok': False}, status=404)

    UserAttempt.objects.create(user=request.user, scenario=scenario, was_correct=was_correct)

    points_earned = 0
    if was_correct:
        points_earned = POINTS_MAP.get(scenario.difficulty, 20)
        profile = request.user.profile
        profile.points += points_earned
        profile.save()
        total_points = profile.points
        level = profile.level
        level_name_en = profile.level_name_en
        level_name_ar = profile.level_name_ar
    else:
        profile = request.user.profile
        total_points = profile.points
        level = profile.level
        level_name_en = profile.level_name_en
        level_name_ar = profile.level_name_ar

    return JsonResponse({
        'ok': True,
        'points_earned': points_earned,
        'total_points': total_points,
        'level': level,
        'level_name_en': level_name_en,
        'level_name_ar': level_name_ar,
    })


# ─── main pages ─────────────────────────────────────────────────────────────

def _random_warning():
    warnings = list(SiteWarning.objects.filter(is_active=True))
    return random.choice(warnings) if warnings else None


def home(request):
    return render(request, 'ar/index.html', {
        'scams': ScamType.objects.all(),
        'warning': _random_warning(),
    })


def about(request):
    return render(request, 'ar/about.html')


def report(request):
    msg = None
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        explanation = request.POST.get('explanation', '').strip()
        is_scam = request.POST.get('is_scam', 'yes') == 'yes'
        image = request.FILES.get('image')
        if title and explanation:
            rep = ScenarioReport(language='ar', title=title, explanation=explanation, is_scam=is_scam)
            if request.user.is_authenticated:
                rep.submitted_by = request.user
            if image:
                rep.image = image
            rep.save()
            msg = 'success'
        else:
            msg = 'error'
    return render(request, 'ar/report.html', {'msg': msg})


def scams(request):
    return render(request, 'ar/scams.html', {'scams': ScamType.objects.all()})


def scam_detail(request, pk):
    return render(request, 'ar/scam_detail.html', {'scam': get_object_or_404(ScamType, pk=pk)})


def home_en(request):
    return render(request, 'en/index.html', {
        'scams': ScamType.objects.all(),
        'warning': _random_warning(),
    })


def about_en(request):
    return render(request, 'en/about.html')


def report_en(request):
    msg = None
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        explanation = request.POST.get('explanation', '').strip()
        is_scam = request.POST.get('is_scam', 'yes') == 'yes'
        image = request.FILES.get('image')
        if title and explanation:
            rep = ScenarioReport(language='en', title=title, explanation=explanation, is_scam=is_scam)
            if request.user.is_authenticated:
                rep.submitted_by = request.user
            if image:
                rep.image = image
            rep.save()
            msg = 'success'
        else:
            msg = 'error'
    return render(request, 'en/report.html', {'msg': msg})


def scams_en(request):
    return render(request, 'en/scams.html', {'scams': ScamType.objects.all()})


def scam_detail_en(request, pk):
    return render(request, 'en/scam_detail.html', {'scam': get_object_or_404(ScamType, pk=pk)})


def simulator_view(request):
    if request.user.is_authenticated:
        scenarios = _get_adaptive_scenarios(request.user)
    else:
        all_s = list(PhishingScenario.objects.all())
        scenarios = random.sample(all_s, min(len(all_s), 10))

    # pre-test baseline: total attempts before this session
    pre_attempts = 0
    pre_accuracy = None
    if request.user.is_authenticated:
        all_attempts = UserAttempt.objects.filter(user=request.user)
        pre_attempts = all_attempts.count()
        if pre_attempts > 0:
            correct = all_attempts.filter(was_correct=True).count()
            pre_accuracy = round(correct / pre_attempts * 100)

    ctx = {
        'scenarios': scenarios,
        'pre_attempts': pre_attempts,
        'pre_accuracy': pre_accuracy,
    }

    if '/ar/' in request.path:
        return render(request, 'ar/simulator.html', ctx)
    return render(request, 'en/simulator.html', ctx)


# ─── profile ─────────────────────────────────────────────────────────────────

@login_required(login_url='/ar/login/')
def profile_view(request):
    lang = _lang(request)
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    messages = {'success': [], 'error': []}

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_username':
            new_username = request.POST.get('username', '').strip()
            if not new_username:
                messages['error'].append('اسم المستخدم مطلوب' if lang == 'ar' else 'Username is required')
            elif new_username == user.username:
                messages['error'].append('هذا هو اسمك الحالي' if lang == 'ar' else 'That is already your username')
            elif User.objects.filter(username=new_username).exists():
                messages['error'].append('اسم المستخدم مستخدم بالفعل' if lang == 'ar' else 'Username already taken')
            else:
                user.username = new_username
                user.save()
                messages['success'].append('تم تحديث اسم المستخدم' if lang == 'ar' else 'Username updated successfully')

        elif action == 'change_password':
            old_pw = request.POST.get('old_password', '')
            new_pw1 = request.POST.get('new_password1', '')
            new_pw2 = request.POST.get('new_password2', '')
            if not user.check_password(old_pw):
                messages['error'].append('كلمة المرور الحالية غير صحيحة' if lang == 'ar' else 'Current password is incorrect')
            elif new_pw1 != new_pw2:
                messages['error'].append('كلمتا المرور غير متطابقتين' if lang == 'ar' else 'Passwords do not match')
            elif len(new_pw1) < 8:
                messages['error'].append('كلمة المرور 8 أحرف على الأقل' if lang == 'ar' else 'Password must be at least 8 characters')
            else:
                user.set_password(new_pw1)
                user.save()
                login(request, user)
                messages['success'].append('تم تغيير كلمة المرور' if lang == 'ar' else 'Password changed successfully')

        elif action == 'delete_history':
            UserAttempt.objects.filter(user=user).delete()
            profile.points = 0
            profile.save()
            messages['success'].append('تم حذف السجل وإعادة النقاط إلى الصفر' if lang == 'ar' else 'History cleared and points reset to zero')

    # ── stats ──
    all_attempts = UserAttempt.objects.filter(user=user).select_related('scenario')
    total = all_attempts.count()
    correct = all_attempts.filter(was_correct=True).count()
    overall_accuracy = round(correct / total * 100) if total > 0 else 0

    by_difficulty = {}
    for diff_key, _, label_ar, label_en in [
        ('easy', None, 'سهل', 'Easy'),
        ('medium', None, 'متوسط', 'Medium'),
        ('hard', None, 'صعب', 'Hard'),
    ]:
        qs = all_attempts.filter(scenario__difficulty=diff_key)
        t = qs.count()
        c = qs.filter(was_correct=True).count()
        by_difficulty[diff_key] = {
            'label_ar': label_ar,
            'label_en': label_en,
            'total': t,
            'correct': c,
            'accuracy': round(c / t * 100) if t > 0 else None,
        }

    # next level info
    next_level = None
    if profile.level < 5:
        nl = LEVEL_THRESHOLDS[profile.level]
        next_level = {'pts_needed': nl[0] - profile.points, 'name_ar': nl[2], 'name_en': nl[3]}

    recent_attempts = all_attempts[:50]

    ctx = {
        'profile': profile,
        'total': total,
        'correct': correct,
        'wrong': total - correct,
        'overall_accuracy': overall_accuracy,
        'by_difficulty': by_difficulty,
        'next_level': next_level,
        'recent_attempts': recent_attempts,
        'messages': messages,
        'joined': user.date_joined,
    }

    tpl = 'ar/profile.html' if lang == 'ar' else 'en/profile.html'
    return render(request, tpl, ctx)


# ─── leaderboard ─────────────────────────────────────────────────────────────

def phishing_list_view(request):
    lang = _lang(request)
    scenarios = PhishingScenario.objects.all().order_by('-id')
    tpl = 'ar/phishing_list.html' if lang == 'ar' else 'en/phishing_list.html'
    return render(request, tpl, {'scenarios': scenarios})


def phishing_detail_view(request, pk):
    lang = _lang(request)
    scenario = get_object_or_404(PhishingScenario, pk=pk)
    # Determine who contributed this scenario
    try:
        report = scenario.source_report
        if report.submitted_by:
            contributor = report.submitted_by.username
        else:
            contributor = 'مجهول' if lang == 'ar' else 'Anonymous'
    except Exception:
        contributor = 'فريق الإدارة' if lang == 'ar' else 'Admin Team'
    tpl = 'ar/phishing_detail.html' if lang == 'ar' else 'en/phishing_detail.html'
    return render(request, tpl, {'scenario': scenario, 'contributor': contributor})


def leaderboard_view(request):
    lang = _lang(request)
    top_profiles = UserProfile.objects.select_related('user').order_by('-points')[:10]

    leaderboard = []
    for profile in top_profiles:
        attempts = UserAttempt.objects.filter(user=profile.user)
        total = attempts.count()
        correct = attempts.filter(was_correct=True).count()
        leaderboard.append({
            'profile': profile,
            'total': total,
            'accuracy': round(correct / total * 100) if total > 0 else 0,
        })

    tpl = 'ar/leaderboard.html' if lang == 'ar' else 'en/leaderboard.html'
    return render(request, tpl, {'leaderboard': leaderboard})


# ─── my reports ──────────────────────────────────────────────────────────────

def my_reports_view(request):
    lang = _lang(request)
    if not request.user.is_authenticated:
        login_url = '/ar/login/' if lang == 'ar' else '/en/login/'
        return redirect(login_url)
    reports = ScenarioReport.objects.filter(
        submitted_by=request.user
    ).order_by('-created_at')
    tpl = 'ar/my_reports.html' if lang == 'ar' else 'en/my_reports.html'
    return render(request, tpl, {'reports': reports})

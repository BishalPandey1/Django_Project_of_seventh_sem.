from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import LoginForm, SignUpForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def home_view(request):
    return render(request, 'accounts/home.html')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'accounts/profile.html')


@login_required
def settings_view(request):
    user = request.user
    if request.method == 'POST':
        if 'update_notifications' in request.POST:
            messages.success(request, 'Notification preferences updated!')
        elif 'change_password' in request.POST:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if not user.check_password(old_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully!')
        return redirect('settings')
    return render(request, 'accounts/settings.html')


@login_required
def lessons_view(request):
    lessons = [
        {
            'title': 'Algebra Fundamentals',
            'description': 'Variables, equations, and expressions',
            'icon': '📐',
            'topics': ['Linear Equations', 'Quadratic Equations', 'Polynomials', 'Factoring', 'Inequalities']
        },
        {
            'title': 'Calculus',
            'description': 'Limits, derivatives, and integrals',
            'icon': '📈',
            'topics': ['Limits & Continuity', 'Derivatives', 'Integration', 'Applications of Derivatives', 'Differential Equations']
        },
        {
            'title': 'Geometry',
            'description': 'Shapes, angles, and proofs',
            'icon': '🔷',
            'topics': ['Triangles & Congruence', 'Circles', 'Area & Volume', 'Coordinate Geometry', 'Transformations']
        },
        {
            'title': 'Trigonometry',
            'description': 'Sine, cosine, and tangent functions',
            'icon': '📊',
            'topics': ['Trigonometric Ratios', 'Unit Circle', 'Graphs of Trig Functions', 'Identities', 'Law of Sines & Cosines']
        },
        {
            'title': 'Statistics & Probability',
            'description': 'Data analysis and probability theory',
            'icon': '🎲',
            'topics': ['Mean, Median, Mode', 'Standard Deviation', 'Probability Distributions', 'Hypothesis Testing', 'Regression Analysis']
        },
        {
            'title': 'Number Theory',
            'description': 'Properties of integers and primes',
            'icon': '🔢',
            'topics': ['Prime Numbers', 'Divisibility', 'GCD & LCM', 'Modular Arithmetic', 'Fermat\'s Theorem']
        },
        {
            'title': 'Linear Algebra',
            'description': 'Vectors, matrices, and transformations',
            'icon': '🧮',
            'topics': ['Matrices & Determinants', 'Vector Spaces', 'Eigenvalues', 'Linear Transformations', 'Systems of Equations']
        },
        {
            'title': 'Discrete Mathematics',
            'description': 'Logic, sets, and combinatorics',
            'icon': '🔗',
            'topics': ['Set Theory', 'Logic & Proofs', 'Combinatorics', 'Graph Theory', 'Recurrence Relations']
        },
    ]
    return render(request, 'accounts/lessons.html', {'lessons': lessons})


LESSONS_CONTENT = {
    'Algebra Fundamentals': {
        'Linear Equations': {
            'definition': 'A linear equation is an algebraic equation in which each term is either a constant or the product of a constant and a single variable. Linear equations graph as straight lines on a coordinate plane.',
            'explanation': 'Linear equations are the foundation of algebra. They represent relationships between variables where the highest power of the variable is 1. The general form is ax + b = 0, where a and b are constants and a ≠ 0.',
            'examples': [
                {'problem': '2x + 3 = 7', 'solution': 'Subtract 3 from both sides: 2x = 4, then divide by 2: x = 2'},
                {'problem': '5y - 10 = 0', 'solution': 'Add 10 to both sides: 5y = 10, then divide by 5: y = 2'},
                {'problem': '3(x - 4) = 12', 'solution': 'Distribute: 3x - 12 = 12, add 12: 3x = 24, divide by 3: x = 8'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><text x="360" y="255" font-size="14" fill="#333">x</text><text x="205" y="15" font-size="14" fill="#333">y</text><line x1="80" y1="220" x2="320" y2="80" stroke="#667eea" stroke-width="3"/><circle cx="140" cy="185" r="5" fill="#764ba2"/><text x="150" y="180" font-size="12" fill="#764ba2">(1, 5)</text><circle cx="260" cy="115" r="5" fill="#764ba2"/><text x="270" y="110" font-size="12" fill="#764ba2">(5, 13)</text><text x="120" y="270" font-size="12" fill="#666">y = 2x + 3</text></svg>',
            'types': [
                {'name': 'Standard Form', 'formula': 'ax + by = c', 'description': 'Where a, b, and c are constants'},
                {'name': 'Slope-Intercept Form', 'formula': 'y = mx + b', 'description': 'm is slope, b is y-intercept'},
                {'name': 'Point-Slope Form', 'formula': 'y - y₁ = m(x - x₁)', 'description': 'Using a point and slope'}
            ],
            'formulas': [
                {'name': 'Slope Formula', 'formula': 'm = (y₂ - y₁) / (x₂ - x₁)'},
                {'name': 'Slope-Intercept', 'formula': 'y = mx + b'},
                {'name': 'Standard Form', 'formula': 'Ax + By = C'}
            ],
            'solved_problems': [
                {'problem': 'Solve: 3x + 7 = 22', 'steps': ['Subtract 7 from both sides: 3x = 15', 'Divide both sides by 3: x = 5', 'Verification: 3(5) + 7 = 15 + 7 = 22 ✓'], 'answer': 'x = 5'},
                {'problem': 'Solve: 2(x - 3) + 4 = 10', 'steps': ['Distribute: 2x - 6 + 4 = 10', 'Simplify: 2x - 2 = 10', 'Add 2: 2x = 12', 'Divide by 2: x = 6'], 'answer': 'x = 6'},
                {'problem': 'Find the slope between (2, 5) and (6, 13)', 'steps': ['Use slope formula: m = (y₂ - y₁)/(x₂ - x₁)', 'm = (13 - 5)/(6 - 2)', 'm = 8/4 = 2'], 'answer': 'm = 2'},
                {'problem': 'Write equation of line with slope 3 passing through (1, 4)', 'steps': ['Use point-slope form: y - y₁ = m(x - x₁)', 'y - 4 = 3(x - 1)', 'y - 4 = 3x - 3', 'y = 3x + 1'], 'answer': 'y = 3x + 1'},
                {'problem': 'Solve: (x/2) + 5 = 9', 'steps': ['Subtract 5: x/2 = 4', 'Multiply both sides by 2: x = 8', 'Verification: 8/2 + 5 = 4 + 5 = 9 ✓'], 'answer': 'x = 8'}
            ]
        },
        'Quadratic Equations': {
            'definition': 'A quadratic equation is a second-degree polynomial equation in a single variable x, with the standard form ax² + bx + c = 0, where a ≠ 0.',
            'explanation': 'Quadratic equations produce parabolic graphs. They can have two real solutions, one repeated solution, or two complex solutions depending on the discriminant (b² - 4ac).',
            'examples': [
                {'problem': 'x² - 5x + 6 = 0', 'solution': 'Factor: (x - 2)(x - 3) = 0, so x = 2 or x = 3'},
                {'problem': '2x² + 4x - 6 = 0', 'solution': 'Divide by 2: x² + 2x - 3 = 0, factor: (x + 3)(x - 1) = 0, so x = -3 or x = 1'},
                {'problem': 'x² = 16', 'solution': 'Take square root: x = ±4'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><path d="M 80 200 Q 200 50 320 200" fill="none" stroke="#667eea" stroke-width="3"/><circle cx="140" cy="200" r="5" fill="#764ba2"/><text x="130" y="220" font-size="12" fill="#764ba2">(2, 0)</text><circle cx="260" cy="200" r="5" fill="#764ba2"/><text x="250" y="220" font-size="12" fill="#764ba2">(3, 0)</text><circle cx="200" cy="125" r="5" fill="#ff4757"/><text x="210" y="120" font-size="12" fill="#ff4757">Vertex (2.5, -0.25)</text><text x="120" y="270" font-size="12" fill="#666">y = x² - 5x + 6</text></svg>',
            'types': [
                {'name': 'Standard Form', 'formula': 'ax² + bx + c = 0', 'description': 'General form of quadratic equation'},
                {'name': 'Vertex Form', 'formula': 'y = a(x - h)² + k', 'description': 'Shows vertex (h, k) directly'},
                {'name': 'Factored Form', 'formula': 'y = a(x - r₁)(x - r₂)', 'description': 'Shows roots r₁ and r₂'}
            ],
            'formulas': [
                {'name': 'Quadratic Formula', 'formula': 'x = (-b ± √(b² - 4ac)) / 2a'},
                {'name': 'Discriminant', 'formula': 'Δ = b² - 4ac'},
                {'name': 'Vertex x-coordinate', 'formula': 'x = -b/2a'},
                {'name': 'Sum of Roots', 'formula': 'r₁ + r₂ = -b/a'},
                {'name': 'Product of Roots', 'formula': 'r₁ × r₂ = c/a'}
            ],
            'solved_problems': [
                {'problem': 'Solve: x² - 7x + 12 = 0', 'steps': ['Factor: Find two numbers that multiply to 12 and add to -7', 'Numbers are -3 and -4', '(x - 3)(x - 4) = 0', 'x = 3 or x = 4'], 'answer': 'x = 3 or x = 4'},
                {'problem': 'Solve using quadratic formula: 2x² + 5x - 3 = 0', 'steps': ['a = 2, b = 5, c = -3', 'x = (-5 ± √(25 + 24)) / 4', 'x = (-5 ± √49) / 4', 'x = (-5 ± 7) / 4', 'x = 2/4 = 1/2 or x = -12/4 = -3'], 'answer': 'x = 1/2 or x = -3'},
                {'problem': 'Find the vertex of y = x² - 6x + 8', 'steps': ['x-coordinate of vertex: x = -b/2a = 6/2 = 3', 'y-coordinate: y = 9 - 18 + 8 = -1', 'Vertex: (3, -1)'], 'answer': 'Vertex: (3, -1)'},
                {'problem': 'Determine the nature of roots: 3x² + 2x + 1 = 0', 'steps': ['Calculate discriminant: Δ = b² - 4ac', 'Δ = 4 - 12 = -8', 'Since Δ < 0, roots are complex'], 'answer': 'Two complex conjugate roots'},
                {'problem': 'Complete the square: x² + 8x + 15 = 0', 'steps': ['Move constant: x² + 8x = -15', 'Add (8/2)² = 16 to both sides: x² + 8x + 16 = 1', '(x + 4)² = 1', 'x + 4 = ±1', 'x = -3 or x = -5'], 'answer': 'x = -3 or x = -5'}
            ]
        },
        'Polynomials': {
            'definition': 'A polynomial is an expression consisting of variables and coefficients, involving only the operations of addition, subtraction, multiplication, and non-negative integer exponents.',
            'explanation': 'Polynomials are classified by their degree (highest power) and number of terms. They form the basis for many mathematical models and are used extensively in science and engineering.',
            'examples': [
                {'problem': '3x³ + 2x² - x + 5', 'solution': 'Degree 3 polynomial (cubic) with 4 terms'},
                {'problem': '(x + 2)(x - 3)', 'solution': 'Expand: x² - 3x + 2x - 6 = x² - x - 6'},
                {'problem': 'x⁴ - 16', 'solution': 'Difference of squares: (x² + 4)(x² - 4) = (x² + 4)(x + 2)(x - 2)'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><path d="M 60 180 Q 120 280 180 200 Q 220 120 260 180 Q 300 240 340 100" fill="none" stroke="#667eea" stroke-width="3"/><circle cx="120" cy="250" r="5" fill="#764ba2"/><text x="110" y="270" font-size="12" fill="#764ba2">x=-2</text><circle cx="200" cy="250" r="5" fill="#764ba2"/><text x="190" y="270" font-size="12" fill="#764ba2">x=0</text><circle cx="280" cy="250" r="5" fill="#764ba2"/><text x="270" y="270" font-size="12" fill="#764ba2">x=2</text><text x="100" y="290" font-size="12" fill="#666">y = x³ - 4x</text></svg>',
            'types': [
                {'name': 'Monomial', 'formula': 'axⁿ', 'description': 'Single term polynomial'},
                {'name': 'Binomial', 'formula': 'axⁿ + bxᵐ', 'description': 'Two term polynomial'},
                {'name': 'Trinomial', 'formula': 'ax² + bx + c', 'description': 'Three term polynomial'},
                {'name': 'Degree Classification', 'formula': 'Linear(1), Quadratic(2), Cubic(3), Quartic(4)', 'description': 'Based on highest exponent'}
            ],
            'formulas': [
                {'name': 'Remainder Theorem', 'formula': 'f(a) = remainder when f(x) is divided by (x - a)'},
                {'name': 'Factor Theorem', 'formula': '(x - a) is a factor if f(a) = 0'},
                {'name': 'Binomial Theorem', 'formula': '(a + b)ⁿ = Σ C(n,k) × aⁿ⁻ᵏ × bᵏ'}
            ],
            'solved_problems': [
                {'problem': 'Add: (3x² + 2x - 5) + (x² - 4x + 7)', 'steps': ['Combine like terms', 'x² terms: 3x² + x² = 4x²', 'x terms: 2x + (-4x) = -2x', 'Constants: -5 + 7 = 2'], 'answer': '4x² - 2x + 2'},
                {'problem': 'Multiply: (x + 3)(x² - 2x + 1)', 'steps': ['Distribute x: x³ - 2x² + x', 'Distribute 3: 3x² - 6x + 3', 'Combine: x³ + x² - 5x + 3'], 'answer': 'x³ + x² - 5x + 3'},
                {'problem': 'Divide: (x³ - 8) ÷ (x - 2)', 'steps': ['Use synthetic division or long division', 'x³ - 8 = (x - 2)(x² + 2x + 4)', 'Quotient: x² + 2x + 4, Remainder: 0'], 'answer': 'x² + 2x + 4'},
                {'problem': 'Find the degree and leading coefficient of 5x⁴ - 3x² + 7x - 1', 'steps': ['Highest power is 4, so degree = 4', 'Coefficient of x⁴ is 5'], 'answer': 'Degree: 4, Leading coefficient: 5'},
                {'problem': 'Evaluate f(x) = 2x³ - x² + 3x - 4 at x = 2', 'steps': ['f(2) = 2(8) - 4 + 6 - 4', 'f(2) = 16 - 4 + 6 - 4', 'f(2) = 14'], 'answer': 'f(2) = 14'}
            ]
        },
        'Factoring': {
            'definition': 'Factoring is the process of breaking down an algebraic expression into a product of simpler expressions (factors) that, when multiplied together, give the original expression.',
            'explanation': 'Factoring is essential for solving equations, simplifying expressions, and finding roots. Common methods include GCF, difference of squares, grouping, and special patterns.',
            'examples': [
                {'problem': 'x² - 9', 'solution': 'Difference of squares: (x + 3)(x - 3)'},
                {'problem': 'x² + 5x + 6', 'solution': 'Find factors of 6 that add to 5: (x + 2)(x + 3)'},
                {'problem': '2x² + 7x + 3', 'solution': 'AC method: (2x + 1)(x + 3)'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Factoring Methods</text><rect x="30" y="60" width="160" height="50" rx="8" fill="#667eea" opacity="0.2"/><text x="110" y="90" font-size="14" fill="#333" text-anchor="middle">GCF Method</text><rect x="210" y="60" width="160" height="50" rx="8" fill="#764ba2" opacity="0.2"/><text x="290" y="90" font-size="14" fill="#333" text-anchor="middle">Difference of Squares</text><rect x="30" y="130" width="160" height="50" rx="8" fill="#667eea" opacity="0.2"/><text x="110" y="160" font-size="14" fill="#333" text-anchor="middle">Grouping</text><rect x="210" y="130" width="160" height="50" rx="8" fill="#764ba2" opacity="0.2"/><text x="290" y="160" font-size="14" fill="#333" text-anchor="middle">Perfect Square</text><rect x="30" y="200" width="160" height="50" rx="8" fill="#667eea" opacity="0.2"/><text x="110" y="230" font-size="14" fill="#333" text-anchor="middle">Sum/Diff of Cubes</text><rect x="210" y="200" width="160" height="50" rx="8" fill="#764ba2" opacity="0.2"/><text x="290" y="230" font-size="14" fill="#333" text-anchor="middle">AC Method</text></svg>',
            'types': [
                {'name': 'Greatest Common Factor', 'formula': 'ab + ac = a(b + c)', 'description': 'Factor out the common term'},
                {'name': 'Difference of Squares', 'formula': 'a² - b² = (a + b)(a - b)', 'description': 'Special pattern for subtraction of squares'},
                {'name': 'Perfect Square Trinomial', 'formula': 'a² ± 2ab + b² = (a ± b)²', 'description': 'Square of a binomial'},
                {'name': 'Sum of Cubes', 'formula': 'a³ + b³ = (a + b)(a² - ab + b²)', 'description': 'Factoring sum of two cubes'},
                {'name': 'Difference of Cubes', 'formula': 'a³ - b³ = (a - b)(a² + ab + b²)', 'description': 'Factoring difference of two cubes'}
            ],
            'formulas': [
                {'name': 'Difference of Squares', 'formula': 'a² - b² = (a + b)(a - b)'},
                {'name': 'Perfect Square', 'formula': 'a² + 2ab + b² = (a + b)²'},
                {'name': 'Sum of Cubes', 'formula': 'a³ + b³ = (a + b)(a² - ab + b²)'},
                {'name': 'Difference of Cubes', 'formula': 'a³ - b³ = (a - b)(a² + ab + b²)'}
            ],
            'solved_problems': [
                {'problem': 'Factor: 6x² + 12x', 'steps': ['Find GCF of 6x² and 12x', 'GCF = 6x', 'Factor out 6x: 6x(x + 2)'], 'answer': '6x(x + 2)'},
                {'problem': 'Factor: x² - 16', 'steps': ['Recognize difference of squares', 'a = x, b = 4', 'Apply: (x + 4)(x - 4)'], 'answer': '(x + 4)(x - 4)'},
                {'problem': 'Factor: x² + 7x + 12', 'steps': ['Find two numbers that multiply to 12 and add to 7', 'Numbers are 3 and 4', '(x + 3)(x + 4)'], 'answer': '(x + 3)(x + 4)'},
                {'problem': 'Factor: 8x³ - 27', 'steps': ['Recognize difference of cubes', 'a = 2x, b = 3', '(2x - 3)(4x² + 6x + 9)'], 'answer': '(2x - 3)(4x² + 6x + 9)'},
                {'problem': 'Factor by grouping: x³ + 2x² + 3x + 6', 'steps': ['Group: (x³ + 2x²) + (3x + 6)', 'Factor each group: x²(x + 2) + 3(x + 2)', 'Factor out common binomial: (x + 2)(x² + 3)'], 'answer': '(x + 2)(x² + 3)'}
            ]
        },
        'Inequalities': {
            'definition': 'An inequality is a mathematical statement that compares two expressions using the symbols < (less than), > (greater than), ≤ (less than or equal to), or ≥ (greater than or equal to).',
            'explanation': 'Inequalities describe ranges of values rather than single solutions. When solving, remember to reverse the inequality sign when multiplying or dividing by a negative number.',
            'examples': [
                {'problem': '2x + 3 > 7', 'solution': 'Subtract 3: 2x > 4, divide by 2: x > 2'},
                {'problem': '-3x ≤ 12', 'solution': 'Divide by -3 (reverse sign): x ≥ -4'},
                {'problem': '|x - 3| < 5', 'solution': '-5 < x - 3 < 5, so -2 < x < 8'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Number Line: x > 2</text><line x1="50" y1="150" x2="350" y2="150" stroke="#333" stroke-width="2"/><circle cx="150" cy="150" r="6" fill="white" stroke="#667eea" stroke-width="3"/><text x="145" y="180" font-size="14" fill="#333" text-anchor="middle">2</text><path d="M 156 150 L 340 150" stroke="#667eea" stroke-width="4"/><polygon points="340,145 350,150 340,155" fill="#667eea"/><text x="200" y="220" font-size="14" fill="#666" text-anchor="middle">Solution: (2, ∞)</text><text x="200" y="260" font-size="12" fill="#999" text-anchor="middle">Open circle means 2 is NOT included</text></svg>',
            'types': [
                {'name': 'Linear Inequality', 'formula': 'ax + b < c or ax + b > c', 'description': 'First-degree inequality'},
                {'name': 'Compound Inequality', 'formula': 'a < x < b', 'description': 'Two inequalities combined'},
                {'name': 'Absolute Value Inequality', 'formula': '|x - a| < b or |x - a| > b', 'description': 'Involving absolute value'},
                {'name': 'Quadratic Inequality', 'formula': 'ax² + bx + c > 0', 'description': 'Second-degree inequality'}
            ],
            'formulas': [
                {'name': 'Addition Property', 'formula': 'If a < b, then a + c < b + c'},
                {'name': 'Multiplication Property', 'formula': 'If a < b and c > 0, then ac < bc'},
                {'name': 'Negative Multiplication', 'formula': 'If a < b and c < 0, then ac > bc (reverse)'},
                {'name': 'Absolute Value', 'formula': '|x| < a means -a < x < a'}
            ],
            'solved_problems': [
                {'problem': 'Solve: 5x - 3 < 2x + 9', 'steps': ['Subtract 2x: 3x - 3 < 9', 'Add 3: 3x < 12', 'Divide by 3: x < 4'], 'answer': 'x < 4 or (-∞, 4)'},
                {'problem': 'Solve: -2(x - 3) ≥ 8', 'steps': ['Distribute: -2x + 6 ≥ 8', 'Subtract 6: -2x ≥ 2', 'Divide by -2 (reverse sign): x ≤ -1'], 'answer': 'x ≤ -1 or (-∞, -1]'},
                {'problem': 'Solve: |2x - 1| ≤ 7', 'steps': ['-7 ≤ 2x - 1 ≤ 7', 'Add 1: -6 ≤ 2x ≤ 8', 'Divide by 2: -3 ≤ x ≤ 4'], 'answer': '[-3, 4]'},
                {'problem': 'Solve: x² - 4 > 0', 'steps': ['Factor: (x + 2)(x - 2) > 0', 'Critical points: x = -2, x = 2', 'Test intervals: x < -2 or x > 2'], 'answer': '(-∞, -2) ∪ (2, ∞)'},
                {'problem': 'Solve: 3 ≤ 2x + 1 < 9', 'steps': ['Subtract 1: 2 ≤ 2x < 8', 'Divide by 2: 1 ≤ x < 4'], 'answer': '[1, 4)'}
            ]
        }
    },
    'Calculus': {
        'Limits & Continuity': {
            'definition': 'A limit describes the value that a function approaches as the input approaches some value. Continuity means a function has no breaks, jumps, or holes in its graph.',
            'explanation': 'Limits are the foundation of calculus. They allow us to understand instantaneous rates of change and areas under curves. A function f(x) is continuous at x = a if lim(x→a) f(x) = f(a).',
            'examples': [
                {'problem': 'lim(x→2) (x² - 4)/(x - 2)', 'solution': 'Factor: (x+2)(x-2)/(x-2) = x+2, so limit = 4'},
                {'problem': 'lim(x→0) sin(x)/x', 'solution': 'This is a standard limit equal to 1'},
                {'problem': 'lim(x→∞) (3x² + 1)/(x² + 2)', 'solution': 'Divide by x²: (3 + 1/x²)/(1 + 2/x²) → 3/1 = 3'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><path d="M 60 240 Q 140 240 180 150 Q 200 100 220 150 Q 260 240 340 240" fill="none" stroke="#667eea" stroke-width="3"/><circle cx="200" cy="100" r="5" fill="white" stroke="#ff4757" stroke-width="3"/><text x="210" y="95" font-size="12" fill="#ff4757">Hole at x=2</text><text x="200" y="270" font-size="12" fill="#666" text-anchor="middle">f(x) = (x²-4)/(x-2)</text><text x="100" y="280" font-size="12" fill="#666">lim(x→2) f(x) = 4</text></svg>',
            'types': [
                {'name': 'Left-Hand Limit', 'formula': 'lim(x→a⁻) f(x)', 'description': 'Approaching from the left'},
                {'name': 'Right-Hand Limit', 'formula': 'lim(x→a⁺) f(x)', 'description': 'Approaching from the right'},
                {'name': 'Two-Sided Limit', 'formula': 'lim(x→a) f(x)', 'description': 'Both sides must agree'},
                {'name': 'Infinite Limit', 'formula': 'lim(x→a) f(x) = ∞', 'description': 'Function grows without bound'}
            ],
            'formulas': [
                {'name': 'Limit of Sum', 'formula': 'lim[f(x) + g(x)] = lim f(x) + lim g(x)'},
                {'name': 'Limit of Product', 'formula': 'lim[f(x) × g(x)] = lim f(x) × lim g(x)'},
                {'name': 'L\'Hopital\'s Rule', 'formula': 'lim f/g = lim f\'/g\' (if 0/0 or ∞/∞)'},
                {'name': 'Squeeze Theorem', 'formula': 'If g ≤ f ≤ h and lim g = lim h = L, then lim f = L'}
            ],
            'solved_problems': [
                {'problem': 'Find lim(x→3) (x² - 9)/(x - 3)', 'steps': ['Factor numerator: (x+3)(x-3)/(x-3)', 'Cancel (x-3): x + 3', 'Substitute x = 3: 3 + 3 = 6'], 'answer': '6'},
                {'problem': 'Find lim(x→0) (√(x+1) - 1)/x', 'steps': ['Multiply by conjugate: (√(x+1)+1)/(√(x+1)+1)', 'Simplify: x/(x(√(x+1)+1))', 'Cancel x: 1/(√(x+1)+1)', 'Substitute x=0: 1/(1+1) = 1/2'], 'answer': '1/2'},
                {'problem': 'Find lim(x→∞) (2x³ + 1)/(x³ - 5)', 'steps': ['Divide numerator and denominator by x³', '(2 + 1/x³)/(1 - 5/x³)', 'As x→∞, 1/x³ → 0 and 5/x³ → 0', 'Result: 2/1 = 2'], 'answer': '2'},
                {'problem': 'Determine if f(x) = (x²-1)/(x-1) is continuous at x=1', 'steps': ['f(1) is undefined (division by zero)', 'lim(x→1) f(x) = lim(x+1) = 2 exists', 'Since f(1) is undefined, not continuous'], 'answer': 'Not continuous at x=1 (removable discontinuity)'},
                {'problem': 'Find lim(x→0) (1 - cos(x))/x²', 'steps': ['Use identity: 1-cos(x) = 2sin²(x/2)', '2sin²(x/2)/x² = (1/2) × [sin(x/2)/(x/2)]²', 'As x→0, sin(x/2)/(x/2) → 1', 'Result: (1/2) × 1² = 1/2'], 'answer': '1/2'}
            ]
        },
        'Derivatives': {
            'definition': 'The derivative of a function measures the rate at which the function value changes with respect to changes in its input. It represents the slope of the tangent line at any point.',
            'explanation': 'Derivatives are fundamental to calculus and have applications in physics, engineering, economics, and more. The derivative f\'(x) gives the instantaneous rate of change of f(x).',
            'examples': [
                {'problem': 'f(x) = x³, find f\'(x)', 'solution': 'Using power rule: f\'(x) = 3x²'},
                {'problem': 'f(x) = sin(x), find f\'(x)', 'solution': 'f\'(x) = cos(x)'},
                {'problem': 'f(x) = eˣ, find f\'(x)', 'solution': 'f\'(x) = eˣ (the derivative of eˣ is itself)'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><path d="M 80 220 Q 140 180 200 120 Q 260 60 320 40" fill="none" stroke="#667eea" stroke-width="3"/><line x1="140" y1="200" x2="260" y2="80" stroke="#ff4757" stroke-width="2" stroke-dasharray="5,5"/><circle cx="200" cy="120" r="6" fill="#764ba2"/><text x="210" y="115" font-size="12" fill="#764ba2">(a, f(a))</text><text x="210" y="140" font-size="11" fill="#ff4757">Tangent line</text><text x="100" y="270" font-size="12" fill="#666">f\'(a) = slope of tangent</text></svg>',
            'types': [
                {'name': 'First Derivative', 'formula': 'f\'(x) or dy/dx', 'description': 'Rate of change of the function'},
                {'name': 'Second Derivative', 'formula': 'f\'\'(x) or d²y/dx²', 'description': 'Rate of change of the derivative (concavity)'},
                {'name': 'Partial Derivative', 'formula': '∂f/∂x', 'description': 'Derivative with respect to one variable'},
                {'name': 'Implicit Derivative', 'formula': 'dy/dx from F(x,y) = 0', 'description': 'When y is not isolated'}
            ],
            'formulas': [
                {'name': 'Power Rule', 'formula': 'd/dx(xⁿ) = nxⁿ⁻¹'},
                {'name': 'Product Rule', 'formula': 'd/dx(fg) = f\'g + fg\''},
                {'name': 'Quotient Rule', 'formula': 'd/dx(f/g) = (f\'g - fg\')/g²'},
                {'name': 'Chain Rule', 'formula': 'd/dx[f(g(x))] = f\'(g(x)) × g\'(x)'}
            ],
            'solved_problems': [
                {'problem': 'Find the derivative of f(x) = 3x⁴ - 2x² + 5x - 1', 'steps': ['Apply power rule to each term', 'd/dx(3x⁴) = 12x³', 'd/dx(-2x²) = -4x', 'd/dx(5x) = 5, d/dx(-1) = 0'], 'answer': 'f\'(x) = 12x³ - 4x + 5'},
                {'problem': 'Find d/dx(x² × sin(x))', 'steps': ['Use product rule: f = x², g = sin(x)', 'f\' = 2x, g\' = cos(x)', 'f\'g + fg\' = 2x·sin(x) + x²·cos(x)'], 'answer': '2x·sin(x) + x²·cos(x)'},
                {'problem': 'Find d/dx(sin(x²))', 'steps': ['Use chain rule: outer = sin(u), inner = u = x²', 'd/du(sin(u)) = cos(u)', 'du/dx = 2x', 'Result: cos(x²) × 2x'], 'answer': '2x·cos(x²)'},
                {'problem': 'Find the equation of tangent to y = x² at x = 3', 'steps': ['Point: (3, 9)', 'Slope: f\'(x) = 2x, f\'(3) = 6', 'Use point-slope: y - 9 = 6(x - 3)', 'y = 6x - 9'], 'answer': 'y = 6x - 9'},
                {'problem': 'Find d/dx((x+1)/(x-1))', 'steps': ['Use quotient rule: f = x+1, g = x-1', 'f\' = 1, g\' = 1', '(1·(x-1) - (x+1)·1)/(x-1)²', '(x-1-x-1)/(x-1)² = -2/(x-1)²'], 'answer': '-2/(x-1)²'}
            ]
        },
        'Integration': {
            'definition': 'Integration is the reverse process of differentiation. It finds the area under a curve or the antiderivative of a function.',
            'explanation': 'The definite integral ∫[a,b] f(x)dx gives the net area between the curve and x-axis from x=a to x=b. The indefinite integral ∫f(x)dx gives the family of antiderivatives.',
            'examples': [
                {'problem': '∫x² dx', 'solution': 'x³/3 + C'},
                {'problem': '∫₀¹ 2x dx', 'solution': '[x²]₀¹ = 1 - 0 = 1'},
                {'problem': '∫cos(x) dx', 'solution': 'sin(x) + C'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><path d="M 80 240 Q 140 200 200 140 Q 260 80 320 60" fill="none" stroke="#667eea" stroke-width="3"/><path d="M 120 250 L 120 200 Q 170 170 220 120 L 220 250 Z" fill="#667eea" opacity="0.3"/><text x="120" y="265" font-size="12" fill="#333" text-anchor="middle">a</text><text x="220" y="265" font-size="12" fill="#333" text-anchor="middle">b</text><text x="170" y="180" font-size="14" fill="#764ba2" text-anchor="middle">Area = ∫[a,b] f(x)dx</text></svg>',
            'types': [
                {'name': 'Indefinite Integral', 'formula': '∫f(x)dx = F(x) + C', 'description': 'Family of antiderivatives'},
                {'name': 'Definite Integral', 'formula': '∫[a,b] f(x)dx = F(b) - F(a)', 'description': 'Net area under curve'},
                {'name': 'Improper Integral', 'formula': '∫[a,∞) f(x)dx', 'description': 'Infinite bounds or discontinuity'}
            ],
            'formulas': [
                {'name': 'Power Rule', 'formula': '∫xⁿ dx = xⁿ⁺¹/(n+1) + C (n≠-1)'},
                {'name': 'Fundamental Theorem', 'formula': '∫[a,b] f(x)dx = F(b) - F(a)'},
                {'name': 'Integration by Parts', 'formula': '∫u dv = uv - ∫v du'},
                {'name': 'Substitution', 'formula': '∫f(g(x))g\'(x)dx = ∫f(u)du'}
            ],
            'solved_problems': [
                {'problem': 'Evaluate ∫(3x² + 2x - 1) dx', 'steps': ['Integrate term by term', '∫3x² dx = x³', '∫2x dx = x²', '∫-1 dx = -x'], 'answer': 'x³ + x² - x + C'},
                {'problem': 'Evaluate ∫₀² (4x - x²) dx', 'steps': ['Find antiderivative: 2x² - x³/3', 'Evaluate at 2: 8 - 8/3 = 16/3', 'Evaluate at 0: 0', 'Result: 16/3 - 0 = 16/3'], 'answer': '16/3'},
                {'problem': 'Evaluate ∫x·eˣ dx', 'steps': ['Use integration by parts', 'u = x, dv = eˣdx', 'du = dx, v = eˣ', 'xeˣ - ∫eˣdx = xeˣ - eˣ + C'], 'answer': 'eˣ(x - 1) + C'},
                {'problem': 'Find the area under y = x² from x=0 to x=3', 'steps': ['Area = ∫₀³ x² dx', 'Antiderivative: x³/3', 'Evaluate: 27/3 - 0 = 9'], 'answer': '9 square units'},
                {'problem': 'Evaluate ∫sin(2x) dx', 'steps': ['Use substitution: u = 2x, du = 2dx', '∫sin(u)·(du/2) = -cos(u)/2 + C', 'Substitute back: -cos(2x)/2 + C'], 'answer': '-cos(2x)/2 + C'}
            ]
        },
        'Applications of Derivatives': {
            'definition': 'Derivatives have numerous practical applications including finding maxima/minima, optimization, related rates, curve sketching, and motion analysis.',
            'explanation': 'The first derivative test helps identify local extrema. The second derivative test determines concavity. These tools are essential for solving real-world optimization problems.',
            'examples': [
                {'problem': 'Find max of f(x) = -x² + 4x', 'solution': 'f\'(x) = -2x + 4 = 0, x = 2, f(2) = 4 (maximum)'},
                {'problem': 'A ball thrown up: h(t) = -5t² + 20t', 'solution': 'Max height when v(t) = h\'(t) = -10t + 20 = 0, t = 2s, h = 20m'},
                {'problem': 'Minimize surface area of box with volume 1000', 'solution': 'Use constraint and derivative to find optimal dimensions'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><path d="M 80 200 Q 140 100 200 80 Q 260 100 320 200" fill="none" stroke="#667eea" stroke-width="3"/><circle cx="200" cy="80" r="6" fill="#ff4757"/><text x="210" y="75" font-size="12" fill="#ff4757">Maximum</text><circle cx="140" cy="140" r="4" fill="#4caf50"/><text x="100" y="135" font-size="11" fill="#4caf50">f\'(x)=0</text><circle cx="260" cy="140" r="4" fill="#4caf50"/><text x="270" y="135" font-size="11" fill="#4caf50">f\'(x)=0</text><text x="200" y="270" font-size="12" fill="#666" text-anchor="middle">Critical points where f\'(x) = 0</text></svg>',
            'types': [
                {'name': 'Optimization', 'formula': 'Find f\'(x) = 0, check f\'\'(x)', 'description': 'Maximize or minimize quantities'},
                {'name': 'Related Rates', 'formula': 'dy/dt = (dy/dx)(dx/dt)', 'description': 'Rates of connected quantities'},
                {'name': 'Curve Sketching', 'formula': 'Use f\' and f\'\' for shape', 'description': 'Analyze function behavior'},
                {'name': 'Linear Approximation', 'formula': 'L(x) = f(a) + f\'(a)(x-a)', 'description': 'Tangent line approximation'}
            ],
            'formulas': [
                {'name': 'First Derivative Test', 'formula': 'f\' changes + to - → max; - to + → min'},
                {'name': 'Second Derivative Test', 'formula': 'f\'\'(c) > 0 → min; f\'\'(c) < 0 → max'},
                {'name': 'Mean Value Theorem', 'formula': 'f\'(c) = (f(b)-f(a))/(b-a) for some c'},
                {'name': 'Newton\'s Method', 'formula': 'xₙ₊₁ = xₙ - f(xₙ)/f\'(xₙ)'}
            ],
            'solved_problems': [
                {'problem': 'Find the maximum of f(x) = x³ - 3x² + 2', 'steps': ['f\'(x) = 3x² - 6x = 3x(x-2)', 'Critical points: x = 0, x = 2', 'f\'\'(x) = 6x - 6', 'f\'\'(0) = -6 < 0 → local max at x=0, f(0)=2'], 'answer': 'Local maximum: (0, 2)'},
                {'problem': 'A rectangle has perimeter 40. Find max area.', 'steps': ['2l + 2w = 40, so w = 20 - l', 'Area = l(20-l) = 20l - l²', 'dA/dl = 20 - 2l = 0, l = 10', 'w = 10, Area = 100'], 'answer': 'Maximum area = 100 (square 10×10)'},
                {'problem': 'Find intervals where f(x) = x³ - 3x is increasing', 'steps': ['f\'(x) = 3x² - 3 = 3(x²-1) = 3(x+1)(x-1)', 'f\'(x) > 0 when x < -1 or x > 1'], 'answer': 'Increasing on (-∞, -1) ∪ (1, ∞)'},
                {'problem': 'Find inflection points of f(x) = x⁴ - 4x³', 'steps': ['f\'(x) = 4x³ - 12x²', 'f\'\'(x) = 12x² - 24x = 12x(x-2)', 'f\'\'(x) = 0 at x = 0, x = 2'], 'answer': 'Inflection points at x = 0 and x = 2'},
                {'problem': 'A ladder 10ft slides down wall. Bottom moves at 2ft/s. How fast does top slide when bottom is 6ft from wall?', 'steps': ['x² + y² = 100, x = 6, y = 8', '2x(dx/dt) + 2y(dy/dt) = 0', '2(6)(2) + 2(8)(dy/dt) = 0', 'dy/dt = -24/16 = -1.5 ft/s'], 'answer': 'Top slides down at 1.5 ft/s'}
            ]
        },
        'Differential Equations': {
            'definition': 'A differential equation is an equation that relates a function with its derivatives. It describes how a quantity changes with respect to one or more variables.',
            'explanation': 'Differential equations model real-world phenomena like population growth, radioactive decay, heat transfer, and motion. Solving them means finding the function that satisfies the equation.',
            'examples': [
                {'problem': 'dy/dx = 2x', 'solution': 'Integrate: y = x² + C'},
                {'problem': 'dy/dx = y', 'solution': 'Separate: dy/y = dx, ln|y| = x, y = Ceˣ'},
                {'problem': 'dy/dx + y = 0', 'solution': 'Solution: y = Ce⁻ˣ'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Slope Field: dy/dx = x</text><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><line x1="100" y1="200" x2="110" y2="190" stroke="#667eea" stroke-width="2"/><line x1="150" y1="200" x2="160" y2="190" stroke="#667eea" stroke-width="2"/><line x1="250" y1="200" x2="260" y2="210" stroke="#667eea" stroke-width="2"/><line x1="300" y1="200" x2="310" y2="210" stroke="#667eea" stroke-width="2"/><line x1="100" y1="150" x2="110" y2="140" stroke="#667eea" stroke-width="2"/><line x1="150" y1="150" x2="160" y2="140" stroke="#667eea" stroke-width="2"/><line x1="250" y1="150" x2="260" y2="160" stroke="#667eea" stroke-width="2"/><line x1="300" y1="150" x2="310" y2="160" stroke="#667eea" stroke-width="2"/><path d="M 100 220 Q 200 120 300 220" fill="none" stroke="#ff4757" stroke-width="2"/><text x="200" y="270" font-size="12" fill="#666" text-anchor="middle">Solution curves follow slope field</text></svg>',
            'types': [
                {'name': 'Separable', 'formula': 'dy/dx = f(x)g(y)', 'description': 'Variables can be separated'},
                {'name': 'Linear First-Order', 'formula': 'dy/dx + P(x)y = Q(x)', 'description': 'Linear in y and y\'', 'description': 'Using integrating factor'},
                {'name': 'Homogeneous', 'formula': 'dy/dx = F(y/x)', 'description': 'Substitution y = vx works'},
                {'name': 'Second-Order Linear', 'formula': 'ay\'\' + by\' + cy = 0', 'description': 'Constant coefficients'}
            ],
            'formulas': [
                {'name': 'Separation of Variables', 'formula': '∫(1/g(y))dy = ∫f(x)dx'},
                {'name': 'Integrating Factor', 'formula': 'μ(x) = e^(∫P(x)dx)'},
                {'name': 'Exponential Growth', 'formula': 'dy/dt = ky → y = y₀eᵏᵗ'},
                {'name': 'Logistic Growth', 'formula': 'dy/dt = ky(1-y/M)'}
            ],
            'solved_problems': [
                {'problem': 'Solve dy/dx = 3x²y', 'steps': ['Separate: dy/y = 3x²dx', 'Integrate: ln|y| = x³ + C', 'y = e^(x³+C) = Ae^(x³)'], 'answer': 'y = Ae^(x³)'},
                {'problem': 'Solve dy/dx + 2y = 4x', 'steps': ['Integrating factor: μ = e^(∫2dx) = e^(2x)', 'Multiply: e^(2x)dy/dx + 2e^(2x)y = 4xe^(2x)', 'd/dx(ye^(2x)) = 4xe^(2x)', 'Integrate: ye^(2x) = 2xe^(2x) - e^(2x) + C'], 'answer': 'y = 2x - 1 + Ce^(-2x)'},
                {'problem': 'Solve dy/dx = (x+1)/y with y(0) = 2', 'steps': ['Separate: y dy = (x+1)dx', 'Integrate: y²/2 = x²/2 + x + C', 'y(0)=2: 2 = 0 + 0 + C, C = 2', 'y² = x² + 2x + 4'], 'answer': 'y = √(x² + 2x + 4)'},
                {'problem': 'Population grows at rate proportional to size. P(0)=100, P(5)=200. Find P(t).', 'steps': ['dP/dt = kP → P = P₀eᵏᵗ', '100e^(5k) = 200, e^(5k) = 2', '5k = ln(2), k = ln(2)/5'], 'answer': 'P(t) = 100 × 2^(t/5)'},
                {'problem': 'Solve y\'\' - 5y\' + 6y = 0', 'steps': ['Characteristic equation: r² - 5r + 6 = 0', '(r-2)(r-3) = 0, r = 2, 3', 'General solution: y = C₁e^(2x) + C₂e^(3x)'], 'answer': 'y = C₁e^(2x) + C₂e^(3x)'}
            ]
        }
    },
    'Geometry': {
        'Triangles & Congruence': {
            'definition': 'A triangle is a three-sided polygon. Two triangles are congruent if they have exactly the same size and shape, meaning all corresponding sides and angles are equal.',
            'explanation': 'Triangles are fundamental in geometry. Congruence can be proven using specific criteria: SSS, SAS, ASA, AAS, and HL (for right triangles).',
            'examples': [
                {'problem': 'Prove two triangles congruent by SSS', 'solution': 'If all three sides of one triangle equal corresponding sides of another, triangles are congruent'},
                {'problem': 'Triangle with sides 3, 4, 5', 'solution': 'This is a right triangle (3² + 4² = 5²), area = 6'},
                {'problem': 'Find missing angle: angles 50°, 70°, ?', 'solution': 'Sum = 180°, missing angle = 180° - 50° - 70° = 60°'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><polygon points="200,50 80,250 320,250" fill="none" stroke="#667eea" stroke-width="3"/><text x="195" y="40" font-size="14" fill="#333" text-anchor="middle">A</text><text x="65" y="265" font-size="14" fill="#333" text-anchor="middle">B</text><text x="335" y="265" font-size="14" fill="#333" text-anchor="middle">C</text><text x="130" y="155" font-size="12" fill="#764ba2">c</text><text x="270" y="155" font-size="12" fill="#764ba2">b</text><text x="200" y="270" font-size="12" fill="#764ba2">a</text><text x="200" y="290" font-size="12" fill="#666" text-anchor="middle">Triangle ABC: a + b + c perimeter</text></svg>',
            'types': [
                {'name': 'Equilateral', 'formula': 'All sides equal, all angles = 60°', 'description': 'Three equal sides and angles'},
                {'name': 'Isosceles', 'formula': 'Two sides equal', 'description': 'Two equal sides, base angles equal'},
                {'name': 'Scalene', 'formula': 'No sides equal', 'description': 'All sides different'},
                {'name': 'Right Triangle', 'formula': 'a² + b² = c²', 'description': 'One angle = 90°'}
            ],
            'formulas': [
                {'name': 'Area', 'formula': 'A = (1/2) × base × height'},
                {'name': 'Heron\'s Formula', 'formula': 'A = √(s(s-a)(s-b)(s-c)), s = (a+b+c)/2'},
                {'name': 'Pythagorean Theorem', 'formula': 'a² + b² = c²'},
                {'name': 'Angle Sum', 'formula': 'A + B + C = 180°'}
            ],
            'solved_problems': [
                {'problem': 'Find area of triangle with base 10 and height 6', 'steps': ['A = (1/2) × base × height', 'A = (1/2) × 10 × 6', 'A = 30'], 'answer': '30 square units'},
                {'problem': 'Find hypotenuse of right triangle with legs 5 and 12', 'steps': ['c² = 5² + 12² = 25 + 144 = 169', 'c = √169 = 13'], 'answer': '13 units'},
                {'problem': 'Prove triangles congruent: AB=DE, BC=EF, ∠B=∠E', 'steps': ['Given: AB = DE, BC = EF, ∠B = ∠E', 'Two sides and included angle equal', 'By SAS congruence criterion', '△ABC ≅ △DEF'], 'answer': '△ABC ≅ △DEF by SAS'},
                {'problem': 'Find angles of isosceles triangle with vertex angle 40°', 'steps': ['Base angles are equal: let each = x', '40° + x + x = 180°', '2x = 140°, x = 70°'], 'answer': 'Base angles: 70° each'},
                {'problem': 'Find area of triangle with sides 7, 8, 9', 'steps': ['s = (7+8+9)/2 = 12', 'A = √(12×5×4×3)', 'A = √720 = 12√5 ≈ 26.83'], 'answer': '12√5 ≈ 26.83 sq units'}
            ]
        },
        'Circles': {
            'definition': 'A circle is the set of all points in a plane that are equidistant from a fixed point called the center. The distance from center to any point is the radius.',
            'explanation': 'Circles have many important properties involving arcs, chords, tangents, and sectors. Key measurements include circumference, area, and various angle relationships.',
            'examples': [
                {'problem': 'Circle with radius 5', 'solution': 'Circumference = 2π(5) = 10π ≈ 31.42, Area = π(25) = 25π ≈ 78.54'},
                {'problem': 'Arc length with r=6, θ=60°', 'solution': 'Arc = (60/360) × 2π(6) = 2π ≈ 6.28'},
                {'problem': 'Sector area with r=4, θ=90°', 'solution': 'Area = (90/360) × π(16) = 4π ≈ 12.57'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><circle cx="200" cy="150" r="100" fill="none" stroke="#667eea" stroke-width="3"/><circle cx="200" cy="150" r="4" fill="#764ba2"/><text x="210" y="145" font-size="14" fill="#764ba2">O</text><line x1="200" y1="150" x2="300" y2="150" stroke="#ff4757" stroke-width="2"/><text x="250" y="140" font-size="12" fill="#ff4757">radius r</text><path d="M 200 150 L 280 90 A 100 100 0 0 0 300 150 Z" fill="#667eea" opacity="0.2"/><text x="250" y="125" font-size="12" fill="#666">sector</text><text x="200" y="270" font-size="12" fill="#666" text-anchor="middle">C = 2πr, A = πr²</text></svg>',
            'types': [
                {'name': 'Chord', 'formula': 'Line segment connecting two points on circle', 'description': 'Diameter is the longest chord'},
                {'name': 'Tangent', 'formula': 'Line touching circle at exactly one point', 'description': 'Perpendicular to radius at point of contact'},
                {'name': 'Secant', 'formula': 'Line intersecting circle at two points', 'description': 'Contains a chord'},
                {'name': 'Arc', 'formula': 'Portion of circumference', 'description': 'Measured in degrees or length'}
            ],
            'formulas': [
                {'name': 'Circumference', 'formula': 'C = 2πr = πd'},
                {'name': 'Area', 'formula': 'A = πr²'},
                {'name': 'Arc Length', 'formula': 'L = (θ/360°) × 2πr'},
                {'name': 'Sector Area', 'formula': 'A = (θ/360°) × πr²'}
            ],
            'solved_problems': [
                {'problem': 'Find circumference of circle with diameter 14', 'steps': ['C = πd = π × 14', 'C = 14π ≈ 43.98'], 'answer': '14π ≈ 43.98 units'},
                {'problem': 'Find area of circle with radius 7', 'steps': ['A = πr² = π × 49', 'A = 49π ≈ 153.94'], 'answer': '49π ≈ 153.94 sq units'},
                {'problem': 'Find arc length: r=10, central angle=72°', 'steps': ['L = (72/360) × 2π(10)', 'L = (1/5) × 20π = 4π'], 'answer': '4π ≈ 12.57 units'},
                {'problem': 'Find area of segment: r=6, θ=120°', 'steps': ['Sector area = (120/360) × π(36) = 12π', 'Triangle area = (1/2)(6)(6)sin(120°) = 9√3', 'Segment = 12π - 9√3'], 'answer': '12π - 9√3 ≈ 22.11 sq units'},
                {'problem': 'Two tangents from external point P touch circle at A and B. If ∠APB = 60°, find ∠AOB.', 'steps': ['OA ⊥ PA and OB ⊥ PB (tangent property)', 'In quadrilateral OAPB: ∠OAP = ∠OBP = 90°', '∠AOB + 60° + 90° + 90° = 360°', '∠AOB = 120°'], 'answer': '∠AOB = 120°'}
            ]
        },
        'Area & Volume': {
            'definition': 'Area measures the space inside a 2D shape. Volume measures the space inside a 3D object. Both are fundamental measurements in geometry.',
            'explanation': 'Understanding area and volume formulas is essential for solving real-world problems involving space, capacity, and material requirements.',
            'examples': [
                {'problem': 'Rectangle 8 × 5', 'solution': 'Area = 8 × 5 = 40 sq units'},
                {'problem': 'Cylinder r=3, h=7', 'solution': 'Volume = π(9)(7) = 63π ≈ 197.92'},
                {'problem': 'Sphere r=4', 'solution': 'Volume = (4/3)π(64) = 256π/3 ≈ 268.08'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="25" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">3D Shapes</text><rect x="30" y="50" width="100" height="80" fill="#667eea" opacity="0.3" stroke="#667eea" stroke-width="2"/><text x="80" y="95" font-size="12" fill="#333" text-anchor="middle">Cuboid</text><text x="80" y="150" font-size="11" fill="#666" text-anchor="middle">V = lwh</text><ellipse cx="280" cy="90" rx="50" ry="30" fill="#764ba2" opacity="0.3" stroke="#764ba2" stroke-width="2"/><line x1="230" y1="90" x2="230" y2="130" stroke="#764ba2" stroke-width="2"/><line x1="330" y1="90" x2="330" y2="130" stroke="#764ba2" stroke-width="2"/><ellipse cx="280" cy="130" rx="50" ry="30" fill="#764ba2" opacity="0.2" stroke="#764ba2" stroke-width="2"/><text x="280" y="175" font-size="12" fill="#333" text-anchor="middle">Cylinder</text><text x="280" y="195" font-size="11" fill="#666" text-anchor="middle">V = πr²h</text><circle cx="130" cy="230" r="35" fill="#667eea" opacity="0.3" stroke="#667eea" stroke-width="2"/><text x="130" y="275" font-size="12" fill="#333" text-anchor="middle">Sphere</text><text x="130" y="290" font-size="11" fill="#666" text-anchor="middle">V = 4/3 πr³</text></svg>',
            'types': [
                {'name': 'Prisms', 'formula': 'V = Base Area × Height', 'description': 'Uniform cross-section'},
                {'name': 'Pyramids', 'formula': 'V = (1/3) × Base Area × Height', 'description': 'Triangular faces meeting at apex'},
                {'name': 'Cylinders', 'formula': 'V = πr²h', 'description': 'Circular cross-section'},
                {'name': 'Spheres', 'formula': 'V = (4/3)πr³', 'description': 'All points equidistant from center'}
            ],
            'formulas': [
                {'name': 'Rectangle Area', 'formula': 'A = l × w'},
                {'name': 'Triangle Area', 'formula': 'A = (1/2)bh'},
                {'name': 'Cylinder Volume', 'formula': 'V = πr²h'},
                {'name': 'Sphere Volume', 'formula': 'V = (4/3)πr³'},
                {'name': 'Cone Volume', 'formula': 'V = (1/3)πr²h'}
            ],
            'solved_problems': [
                {'problem': 'Find volume of cylinder: r=5, h=12', 'steps': ['V = πr²h', 'V = π × 25 × 12', 'V = 300π'], 'answer': '300π ≈ 942.48 cubic units'},
                {'problem': 'Find surface area of sphere: r=7', 'steps': ['SA = 4πr²', 'SA = 4π × 49', 'SA = 196π'], 'answer': '196π ≈ 615.75 sq units'},
                {'problem': 'Find volume of cone: r=6, h=10', 'steps': ['V = (1/3)πr²h', 'V = (1/3)π × 36 × 10', 'V = 120π'], 'answer': '120π ≈ 376.99 cubic units'},
                {'problem': 'Find area of trapezoid: bases 8 and 12, height 5', 'steps': ['A = (1/2)(b₁ + b₂)h', 'A = (1/2)(8 + 12) × 5', 'A = (1/2)(20)(5) = 50'], 'answer': '50 sq units'},
                {'problem': 'Find volume of rectangular prism: 4 × 6 × 8', 'steps': ['V = lwh', 'V = 4 × 6 × 8', 'V = 192'], 'answer': '192 cubic units'}
            ]
        },
        'Coordinate Geometry': {
            'definition': 'Coordinate geometry (analytic geometry) uses algebraic equations to describe geometric figures on a coordinate plane with x and y axes.',
            'explanation': 'By assigning coordinates to points, we can use algebra to solve geometric problems including distances, midpoints, slopes, and equations of lines and curves.',
            'examples': [
                {'problem': 'Distance between (1,2) and (4,6)', 'solution': 'd = √((4-1)² + (6-2)²) = √(9+16) = √25 = 5'},
                {'problem': 'Midpoint of (2,3) and (8,7)', 'solution': 'M = ((2+8)/2, (3+7)/2) = (5, 5)'},
                {'problem': 'Slope through (1,3) and (5,11)', 'solution': 'm = (11-3)/(5-1) = 8/4 = 2'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><text x="360" y="255" font-size="14" fill="#333">x</text><text x="205" y="15" font-size="14" fill="#333">y</text><circle cx="120" cy="180" r="5" fill="#764ba2"/><text x="100" y="175" font-size="12" fill="#764ba2">(1,2)</text><circle cx="280" cy="100" r="5" fill="#764ba2"/><text x="290" y="95" font-size="12" fill="#764ba2">(4,6)</text><line x1="120" y1="180" x2="280" y2="100" stroke="#667eea" stroke-width="2"/><text x="180" y="130" font-size="12" fill="#666">d = 5</text></svg>',
            'types': [
                {'name': 'Point', 'formula': '(x, y)', 'description': 'Location on coordinate plane'},
                {'name': 'Line', 'formula': 'y = mx + b', 'description': 'Straight line with slope m'},
                {'name': 'Circle', 'formula': '(x-h)² + (y-k)² = r²', 'description': 'Center (h,k), radius r'},
                {'name': 'Parabola', 'formula': 'y = ax² + bx + c', 'description': 'U-shaped curve'}
            ],
            'formulas': [
                {'name': 'Distance', 'formula': 'd = √((x₂-x₁)² + (y₂-y₁)²)'},
                {'name': 'Midpoint', 'formula': 'M = ((x₁+x₂)/2, (y₁+y₂)/2)'},
                {'name': 'Slope', 'formula': 'm = (y₂-y₁)/(x₂-x₁)'},
                {'name': 'Point-Slope', 'formula': 'y - y₁ = m(x - x₁)'}
            ],
            'solved_problems': [
                {'problem': 'Find distance between (3,4) and (7,1)', 'steps': ['d = √((7-3)² + (1-4)²)', 'd = √(16 + 9) = √25', 'd = 5'], 'answer': '5 units'},
                {'problem': 'Find equation of line through (1,2) with slope 3', 'steps': ['y - y₁ = m(x - x₁)', 'y - 2 = 3(x - 1)', 'y = 3x - 1'], 'answer': 'y = 3x - 1'},
                {'problem': 'Find center and radius of (x-2)² + (y+3)² = 25', 'steps': ['Compare with (x-h)² + (y-k)² = r²', 'h = 2, k = -3, r² = 25', 'Center: (2, -3), Radius: 5'], 'answer': 'Center: (2, -3), Radius: 5'},
                {'problem': 'Are lines y = 2x + 1 and y = -x/2 + 3 perpendicular?', 'steps': ['Slope of first line: m₁ = 2', 'Slope of second line: m₂ = -1/2', 'm₁ × m₂ = 2 × (-1/2) = -1', 'Product = -1, so perpendicular'], 'answer': 'Yes, they are perpendicular'},
                {'problem': 'Find area of triangle with vertices (0,0), (4,0), (0,3)', 'steps': ['Base = 4, Height = 3', 'A = (1/2) × 4 × 3', 'A = 6'], 'answer': '6 sq units'}
            ]
        },
        'Transformations': {
            'definition': 'A transformation is a function that maps points of a pre-image to its image. The four basic types are translation, rotation, reflection, and dilation.',
            'explanation': 'Transformations change the position, size, or orientation of geometric figures while preserving certain properties. Rigid transformations preserve size and shape.',
            'examples': [
                {'problem': 'Translate (2,3) by vector (4,-1)', 'solution': 'New point: (2+4, 3+(-1)) = (6, 2)'},
                {'problem': 'Reflect (3,4) over x-axis', 'solution': '(x, y) → (x, -y), so (3, -4)'},
                {'problem': 'Rotate (1,0) by 90° counterclockwise', 'solution': '(x, y) → (-y, x), so (0, 1)'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><polygon points="120,200 160,140 180,200" fill="#667eea" opacity="0.4" stroke="#667eea" stroke-width="2"/><polygon points="240,200 200,140 180,200" fill="#764ba2" opacity="0.4" stroke="#764ba2" stroke-width="2"/><text x="150" y="220" font-size="12" fill="#667eea">Original</text><text x="230" y="220" font-size="12" fill="#764ba2">Reflected</text><text x="200" y="270" font-size="12" fill="#666" text-anchor="middle">Reflection over y-axis</text></svg>',
            'types': [
                {'name': 'Translation', 'formula': '(x, y) → (x + a, y + b)', 'description': 'Slide without rotation'},
                {'name': 'Rotation', 'formula': '(x, y) → (-y, x) for 90°', 'description': 'Turn around a point'},
                {'name': 'Reflection', 'formula': '(x, y) → (x, -y) over x-axis', 'description': 'Flip over a line'},
                {'name': 'Dilation', 'formula': '(x, y) → (kx, ky)', 'description': 'Scale by factor k'}
            ],
            'formulas': [
                {'name': 'Translation', 'formula': 'T(x, y) = (x + a, y + b)'},
                {'name': 'Rotation 90° CCW', 'formula': 'R(x, y) = (-y, x)'},
                {'name': 'Reflection x-axis', 'formula': 'Ref(x, y) = (x, -y)'},
                {'name': 'Dilation', 'formula': 'D(x, y) = (kx, ky)'}
            ],
            'solved_problems': [
                {'problem': 'Translate triangle A(1,1), B(3,1), C(2,4) by (2,3)', 'steps': ['Add (2,3) to each vertex', 'A\' = (1+2, 1+3) = (3, 4)', 'B\' = (3+2, 1+3) = (5, 4)', 'C\' = (2+2, 4+3) = (4, 7)'], 'answer': 'A\'(3,4), B\'(5,4), C\'(4,7)'},
                {'problem': 'Reflect point (5, -2) over y-axis', 'steps': ['Reflection over y-axis: (x, y) → (-x, y)', '(-5, -2)'], 'answer': '(-5, -2)'},
                {'problem': 'Rotate (3, 1) by 180° about origin', 'steps': ['180° rotation: (x, y) → (-x, -y)', '(-3, -1)'], 'answer': '(-3, -1)'},
                {'problem': 'Dilate (2, 4) by scale factor 3', 'steps': ['Dilation: (x, y) → (kx, ky)', '(3×2, 3×4) = (6, 12)'], 'answer': '(6, 12)'},
                {'problem': 'Find the image of y = 2x after reflection over x-axis', 'steps': ['Reflection over x-axis: y → -y', '-y = 2x', 'y = -2x'], 'answer': 'y = -2x'}
            ]
        }
    },
    'Trigonometry': {
        'Trigonometric Ratios': {
            'definition': 'Trigonometric ratios are relationships between the angles and sides of a right triangle. The three primary ratios are sine, cosine, and tangent.',
            'explanation': 'In a right triangle, sin(θ) = opposite/hypotenuse, cos(θ) = adjacent/hypotenuse, tan(θ) = opposite/adjacent. These ratios are fundamental for solving triangles.',
            'examples': [
                {'problem': 'Right triangle: opposite=3, hypotenuse=5', 'solution': 'sin(θ) = 3/5 = 0.6, θ ≈ 36.87°'},
                {'problem': 'adjacent=4, opposite=3', 'solution': 'tan(θ) = 3/4 = 0.75, θ ≈ 36.87°'},
                {'problem': 'hypotenuse=10, θ=30°', 'solution': 'opposite = 10×sin(30°) = 10×0.5 = 5'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><polygon points="80,250 320,250 320,100" fill="none" stroke="#667eea" stroke-width="3"/><text x="65" y="265" font-size="14" fill="#333" text-anchor="middle">A</text><text x="335" y="265" font-size="14" fill="#333" text-anchor="middle">B</text><text x="335" y="95" font-size="14" fill="#333" text-anchor="middle">C</text><text x="200" y="270" font-size="12" fill="#764ba2">adjacent (b)</text><text x="345" y="180" font-size="12" fill="#764ba2">opp (a)</text><text x="180" y="160" font-size="12" fill="#764ba2">hyp (c)</text><text x="95" y="240" font-size="14" fill="#ff4757">θ</text><text x="200" y="290" font-size="12" fill="#666" text-anchor="middle">sin θ = opp/hyp, cos θ = adj/hyp, tan θ = opp/adj</text></svg>',
            'types': [
                {'name': 'Sine', 'formula': 'sin(θ) = opposite/hypotenuse', 'description': 'Ratio of opposite to hypotenuse'},
                {'name': 'Cosine', 'formula': 'cos(θ) = adjacent/hypotenuse', 'description': 'Ratio of adjacent to hypotenuse'},
                {'name': 'Tangent', 'formula': 'tan(θ) = opposite/adjacent', 'description': 'Ratio of opposite to adjacent'},
                {'name': 'Reciprocal Ratios', 'formula': 'csc = 1/sin, sec = 1/cos, cot = 1/tan', 'description': 'Reciprocal trigonometric functions'}
            ],
            'formulas': [
                {'name': 'SOH-CAH-TOA', 'formula': 'sin=O/H, cos=A/H, tan=O/A'},
                {'name': 'Pythagorean Identity', 'formula': 'sin²θ + cos²θ = 1'},
                {'name': 'Tangent Identity', 'formula': 'tan(θ) = sin(θ)/cos(θ)'},
                {'name': 'Law of Sines', 'formula': 'a/sin(A) = b/sin(B) = c/sin(C)'}
            ],
            'solved_problems': [
                {'problem': 'Find sin(θ) if opposite=5, hypotenuse=13', 'steps': ['sin(θ) = opposite/hypotenuse', 'sin(θ) = 5/13 ≈ 0.3846'], 'answer': 'sin(θ) = 5/13 ≈ 0.3846'},
                {'problem': 'Find the height of a building: angle=45°, distance=50m', 'steps': ['tan(45°) = height/50', '1 = height/50', 'height = 50m'], 'answer': '50 meters'},
                {'problem': 'Find cos(θ) if sin(θ) = 3/5', 'steps': ['sin²θ + cos²θ = 1', '(3/5)² + cos²θ = 1', 'cos²θ = 1 - 9/25 = 16/25', 'cos(θ) = 4/5'], 'answer': 'cos(θ) = 4/5'},
                {'problem': 'A ladder 12ft long makes 60° with ground. How high does it reach?', 'steps': ['sin(60°) = height/12', 'height = 12 × sin(60°)', 'height = 12 × √3/2 = 6√3'], 'answer': '6√3 ≈ 10.39 feet'},
                {'problem': 'Find all trig ratios if tan(θ) = 4/3', 'steps': ['opp=4, adj=3, hyp=√(16+9)=5', 'sin(θ) = 4/5', 'cos(θ) = 3/5', 'csc=5/4, sec=5/3, cot=3/4'], 'answer': 'sin=4/5, cos=3/5, tan=4/3, csc=5/4, sec=5/3, cot=3/4'}
            ]
        },
        'Unit Circle': {
            'definition': 'The unit circle is a circle with radius 1 centered at the origin. It provides a geometric way to define trigonometric functions for all real numbers.',
            'explanation': 'On the unit circle, the coordinates of any point are (cos θ, sin θ). The unit circle extends trigonometric functions beyond right triangles to all angles.',
            'examples': [
                {'problem': 'Find cos(π/3) and sin(π/3)', 'solution': 'cos(π/3) = 1/2, sin(π/3) = √3/2'},
                {'problem': 'Find tan(π/4)', 'solution': 'tan(π/4) = sin(π/4)/cos(π/4) = 1'},
                {'problem': 'Find sin(5π/6)', 'solution': 'sin(5π/6) = 1/2 (reference angle π/6, quadrant II)'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><circle cx="200" cy="150" r="100" fill="none" stroke="#667eea" stroke-width="2"/><line x1="50" y1="150" x2="350" y2="150" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><line x1="200" y1="150" x2="287" y2="100" stroke="#ff4757" stroke-width="2"/><circle cx="287" cy="100" r="4" fill="#764ba2"/><text x="295" y="95" font-size="11" fill="#764ba2">(cos θ, sin θ)</text><text x="250" y="120" font-size="11" fill="#ff4757">θ=60°</text><text x="310" y="155" font-size="12" fill="#333">(1, 0)</text><text x="205" y="45" font-size="12" fill="#333">(0, 1)</text><text x="170" y="155" font-size="12" fill="#333">(-1, 0)</text><text x="205" y="265" font-size="12" fill="#333">(0, -1)</text><text x="200" y="290" font-size="12" fill="#666" text-anchor="middle">x² + y² = 1</text></svg>',
            'types': [
                {'name': 'Quadrant I', 'formula': '0° to 90°: all positive', 'description': 'sin, cos, tan all positive'},
                {'name': 'Quadrant II', 'formula': '90° to 180°: sin positive', 'description': 'Only sine is positive'},
                {'name': 'Quadrant III', 'formula': '180° to 270°: tan positive', 'description': 'Only tangent is positive'},
                {'name': 'Quadrant IV', 'formula': '270° to 360°: cos positive', 'description': 'Only cosine is positive'}
            ],
            'formulas': [
                {'name': 'Unit Circle Equation', 'formula': 'x² + y² = 1'},
                {'name': 'Coordinates', 'formula': '(cos θ, sin θ)'},
                {'name': 'Reference Angle', 'formula': 'Smallest angle to x-axis'},
                {'name': 'Periodicity', 'formula': 'sin(θ+2π) = sin(θ), cos(θ+2π) = cos(θ)'}
            ],
            'solved_problems': [
                {'problem': 'Find exact values: sin(π/6), cos(π/6)', 'steps': ['π/6 = 30°', 'sin(30°) = 1/2', 'cos(30°) = √3/2'], 'answer': 'sin(π/6) = 1/2, cos(π/6) = √3/2'},
                {'problem': 'Find sin(2π/3)', 'steps': ['2π/3 = 120° (Quadrant II)', 'Reference angle = π/3 = 60°', 'sin(120°) = sin(60°) = √3/2'], 'answer': '√3/2'},
                {'problem': 'Find cos(7π/4)', 'steps': ['7π/4 = 315° (Quadrant IV)', 'Reference angle = π/4 = 45°', 'cos(315°) = cos(45°) = √2/2'], 'answer': '√2/2'},
                {'problem': 'Find tan(5π/3)', 'steps': ['5π/3 = 300° (Quadrant IV)', 'Reference angle = π/3 = 60°', 'tan(300°) = -tan(60°) = -√3'], 'answer': '-√3'},
                {'problem': 'Evaluate sin²(π/4) + cos²(π/4)', 'steps': ['sin(π/4) = √2/2, cos(π/4) = √2/2', '(√2/2)² + (√2/2)²', '1/2 + 1/2 = 1'], 'answer': '1 (verifies Pythagorean identity)'}
            ]
        },
        'Graphs of Trig Functions': {
            'definition': 'Trigonometric functions produce periodic wave patterns when graphed. Understanding their graphs helps visualize amplitude, period, phase shift, and vertical shift.',
            'explanation': 'The sine and cosine functions have period 2π and amplitude 1. Transformations change these properties: y = A·sin(B(x-C)) + D where A=amplitude, B affects period, C=phase shift, D=vertical shift.',
            'examples': [
                {'problem': 'Graph y = 2sin(x)', 'solution': 'Amplitude = 2, Period = 2π'},
                {'problem': 'Graph y = cos(2x)', 'solution': 'Amplitude = 1, Period = π'},
                {'problem': 'Graph y = sin(x - π/2)', 'solution': 'Phase shift right by π/2, same as -cos(x)'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><line x1="50" y1="150" x2="350" y2="150" stroke="#333" stroke-width="1"/><path d="M 50 150 Q 90 50 130 150 Q 170 250 210 150 Q 250 50 290 150 Q 330 250 350 150" fill="none" stroke="#667eea" stroke-width="2"/><path d="M 50 150 Q 70 100 90 150 Q 110 200 130 150 Q 150 100 170 150 Q 190 200 210 150 Q 230 100 250 150 Q 270 200 290 150 Q 310 100 330 150 Q 340 175 350 150" fill="none" stroke="#764ba2" stroke-width="2" stroke-dasharray="5,3"/><text x="200" y="280" font-size="12" fill="#666" text-anchor="middle">Blue: y=sin(x), Purple: y=cos(x)</text><text x="30" y="55" font-size="11" fill="#667eea">1</text><text x="30" y="255" font-size="11" fill="#667eea">-1</text></svg>',
            'types': [
                {'name': 'Sine Wave', 'formula': 'y = sin(x)', 'description': 'Starts at origin, period 2π'},
                {'name': 'Cosine Wave', 'formula': 'y = cos(x)', 'description': 'Starts at max, period 2π'},
                {'name': 'Tangent', 'formula': 'y = tan(x)', 'description': 'Period π, vertical asymptotes'},
                {'name': 'Transformed', 'formula': 'y = A·sin(B(x-C)) + D', 'description': 'General form with transformations'}
            ],
            'formulas': [
                {'name': 'Amplitude', 'formula': '|A|'},
                {'name': 'Period', 'formula': '2π/|B| for sin/cos, π/|B| for tan'},
                {'name': 'Phase Shift', 'formula': 'C (right if positive)'},
                {'name': 'Vertical Shift', 'formula': 'D (up if positive)'}
            ],
            'solved_problems': [
                {'problem': 'Find amplitude and period of y = 3sin(2x)', 'steps': ['Amplitude = |3| = 3', 'Period = 2π/|2| = π'], 'answer': 'Amplitude: 3, Period: π'},
                {'problem': 'Describe y = 2cos(x - π/4) + 1', 'steps': ['Amplitude = 2', 'Period = 2π', 'Phase shift = π/4 right', 'Vertical shift = 1 up'], 'answer': 'Amp=2, Period=2π, Shift right π/4, Up 1'},
                {'problem': 'Find the period of y = tan(3x)', 'steps': ['Period of tan = π/|B|', 'Period = π/3'], 'answer': 'π/3'},
                {'problem': 'Write equation: amplitude 4, period π, no shift', 'steps': ['A = 4, Period = 2π/B = π', 'B = 2', 'y = 4sin(2x) or y = 4cos(2x)'], 'answer': 'y = 4sin(2x)'},
                {'problem': 'Find max and min of y = -2sin(x) + 3', 'steps': ['Amplitude = 2, vertical shift = 3', 'Max = 3 + 2 = 5', 'Min = 3 - 2 = 1'], 'answer': 'Max: 5, Min: 1'}
            ]
        },
        'Identities': {
            'definition': 'Trigonometric identities are equations involving trigonometric functions that are true for all values of the variables. They are used to simplify expressions and solve equations.',
            'explanation': 'Key identities include Pythagorean, double-angle, half-angle, sum and difference formulas. These are essential tools for simplifying complex trigonometric expressions.',
            'examples': [
                {'problem': 'Verify: sin²θ + cos²θ = 1', 'solution': 'This is the fundamental Pythagorean identity'},
                {'problem': 'Simplify: sin(2θ)', 'solution': 'sin(2θ) = 2sin(θ)cos(θ)'},
                {'problem': 'Find cos(75°)', 'solution': 'cos(45°+30°) = cos45°cos30° - sin45°sin30° = (√6-√2)/4'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Key Trigonometric Identities</text><rect x="20" y="50" width="360" height="40" rx="8" fill="#667eea" opacity="0.15"/><text x="200" y="75" font-size="14" fill="#333" text-anchor="middle">sin²θ + cos²θ = 1</text><rect x="20" y="100" width="360" height="40" rx="8" fill="#764ba2" opacity="0.15"/><text x="200" y="125" font-size="14" fill="#333" text-anchor="middle">sin(2θ) = 2sin(θ)cos(θ)</text><rect x="20" y="150" width="360" height="40" rx="8" fill="#667eea" opacity="0.15"/><text x="200" y="175" font-size="14" fill="#333" text-anchor="middle">cos(2θ) = cos²θ - sin²θ</text><rect x="20" y="200" width="360" height="40" rx="8" fill="#764ba2" opacity="0.15"/><text x="200" y="225" font-size="14" fill="#333" text-anchor="middle">tan(θ) = sin(θ)/cos(θ)</text><rect x="20" y="250" width="360" height="40" rx="8" fill="#667eea" opacity="0.15"/><text x="200" y="275" font-size="14" fill="#333" text-anchor="middle">1 + tan²θ = sec²θ</text></svg>',
            'types': [
                {'name': 'Pythagorean', 'formula': 'sin²θ + cos²θ = 1', 'description': 'Fundamental identity'},
                {'name': 'Double Angle', 'formula': 'sin(2θ) = 2sin(θ)cos(θ)', 'description': 'Angle doubling formulas'},
                {'name': 'Half Angle', 'formula': 'sin(θ/2) = ±√((1-cosθ)/2)', 'description': 'Angle halving formulas'},
                {'name': 'Sum/Difference', 'formula': 'sin(A±B) = sinAcosB ± cosAsinB', 'description': 'Adding/subtracting angles'}
            ],
            'formulas': [
                {'name': 'Pythagorean', 'formula': 'sin²θ + cos²θ = 1'},
                {'name': 'Double Angle Sine', 'formula': 'sin(2θ) = 2sin(θ)cos(θ)'},
                {'name': 'Double Angle Cosine', 'formula': 'cos(2θ) = cos²θ - sin²θ'},
                {'name': 'Sum Formula', 'formula': 'sin(A+B) = sinAcosB + cosAsinB'}
            ],
            'solved_problems': [
                {'problem': 'Prove: (1 - cos²θ)/sin(θ) = sin(θ)', 'steps': ['Use sin²θ + cos²θ = 1', '1 - cos²θ = sin²θ', 'sin²θ/sin(θ) = sin(θ)'], 'answer': 'Proved: sin(θ) = sin(θ)'},
                {'problem': 'Find sin(2θ) if sin(θ) = 3/5 and θ in QI', 'steps': ['cos(θ) = √(1 - 9/25) = 4/5', 'sin(2θ) = 2sin(θ)cos(θ)', 'sin(2θ) = 2 × 3/5 × 4/5 = 24/25'], 'answer': '24/25'},
                {'problem': 'Simplify: cos⁴θ - sin⁴θ', 'steps': ['Factor as difference of squares', '(cos²θ + sin²θ)(cos²θ - sin²θ)', '1 × cos(2θ) = cos(2θ)'], 'answer': 'cos(2θ)'},
                {'problem': 'Find cos(15°) using half-angle', 'steps': ['15° = 30°/2', 'cos(15°) = √((1+cos30°)/2)', 'cos(15°) = √((1+√3/2)/2) = √(2+√3)/2'], 'answer': '√(2+√3)/2 ≈ 0.9659'},
                {'problem': 'Prove: tan(θ) + cot(θ) = sec(θ)csc(θ)', 'steps': ['tan(θ) + cot(θ) = sin/cos + cos/sin', '= (sin²θ + cos²θ)/(sin·cos)', '= 1/(sin·cos) = sec·csc'], 'answer': 'Proved'}
            ]
        },
        'Law of Sines & Cosines': {
            'definition': 'The Law of Sines and Law of Cosines are formulas for solving any triangle (not just right triangles) given certain combinations of sides and angles.',
            'explanation': 'Law of Sines is used when you know AAS, ASA, or SSA. Law of Cosines is used for SAS or SSS. Together they solve any triangle problem.',
            'examples': [
                {'problem': 'Triangle: A=30°, B=45°, a=10. Find b.', 'solution': 'b/sin(45°) = 10/sin(30°), b = 10√2 ≈ 14.14'},
                {'problem': 'SAS: a=5, b=7, C=60°. Find c.', 'solution': 'c² = 25+49-70cos(60°) = 74-35 = 39, c = √39 ≈ 6.24'},
                {'problem': 'SSS: a=3, b=4, c=5. Find angle C.', 'steps': ['cos(C) = (9+16-25)/(2×3×4) = 0', 'C = 90° (right triangle)']}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><polygon points="100,250 300,250 200,80" fill="none" stroke="#667eea" stroke-width="3"/><text x="90" y="265" font-size="14" fill="#333" text-anchor="middle">B</text><text x="310" y="265" font-size="14" fill="#333" text-anchor="middle">C</text><text x="200" y="70" font-size="14" fill="#333" text-anchor="middle">A</text><text x="140" y="270" font-size="12" fill="#764ba2">a</text><text x="270" y="170" font-size="12" fill="#764ba2">b</text><text x="130" y="160" font-size="12" fill="#764ba2">c</text><text x="200" y="290" font-size="12" fill="#666" text-anchor="middle">a/sin(A) = b/sin(B) = c/sin(C)</text></svg>',
            'types': [
                {'name': 'Law of Sines', 'formula': 'a/sin(A) = b/sin(B) = c/sin(C)', 'description': 'For AAS, ASA, SSA cases'},
                {'name': 'Law of Cosines', 'formula': 'c² = a² + b² - 2ab·cos(C)', 'description': 'For SAS, SSS cases'},
                {'name': 'Ambiguous Case', 'formula': 'SSA may give 0, 1, or 2 solutions', 'description': 'Check height h = b·sin(A)'},
                {'name': 'Area Formula', 'formula': 'Area = (1/2)ab·sin(C)', 'description': 'Area using two sides and included angle'}
            ],
            'formulas': [
                {'name': 'Law of Sines', 'formula': 'a/sin(A) = b/sin(B) = c/sin(C)'},
                {'name': 'Law of Cosines', 'formula': 'c² = a² + b² - 2ab·cos(C)'},
                {'name': 'Area (SAS)', 'formula': 'Area = (1/2)ab·sin(C)'},
                {'name': 'Heron\'s Formula', 'formula': 'A = √(s(s-a)(s-b)(s-c))'}
            ],
            'solved_problems': [
                {'problem': 'Solve triangle: A=40°, B=60°, c=12', 'steps': ['C = 180° - 40° - 60° = 80°', 'a/sin(40°) = 12/sin(80°)', 'a = 12 × sin(40°)/sin(80°) ≈ 7.83', 'b = 12 × sin(60°)/sin(80°) ≈ 10.56'], 'answer': 'C=80°, a≈7.83, b≈10.56'},
                {'problem': 'Find largest angle of triangle with sides 7, 9, 12', 'steps': ['Largest angle opposite longest side (12)', 'cos(C) = (49+81-144)/(2×7×9)', 'cos(C) = -14/126 = -1/9', 'C = arccos(-1/9) ≈ 96.38°'], 'answer': 'C ≈ 96.38°'},
                {'problem': 'Find area: a=8, b=10, C=45°', 'steps': ['Area = (1/2)ab·sin(C)', 'Area = (1/2)(8)(10)sin(45°)', 'Area = 40 × √2/2 = 20√2'], 'answer': '20√2 ≈ 28.28 sq units'},
                {'problem': 'SSA case: A=30°, a=5, b=8. How many solutions?', 'steps': ['h = b·sin(A) = 8 × 0.5 = 4', 'a = 5 > h = 4 and a < b = 8', 'Two solutions exist'], 'answer': 'Two triangles possible'},
                {'problem': 'Find distance across lake: angles 45° and 60° from ends of 100m baseline', 'steps': ['Third angle = 180° - 45° - 60° = 75°', 'd/sin(75°) = 100/sin(75°)', 'd = 100m (baseline IS the distance)'], 'answer': 'Use Law of Sines for other distances'}
            ]
        }
    },
    'Statistics & Probability': {
        'Mean, Median, Mode': {
            'definition': 'Mean is the average of all values. Median is the middle value when data is ordered. Mode is the most frequently occurring value. These are measures of central tendency.',
            'explanation': 'These three measures describe the center of a dataset. Each has advantages depending on the data distribution and presence of outliers.',
            'examples': [
                {'problem': 'Data: 2, 4, 4, 6, 8', 'solution': 'Mean = 24/5 = 4.8, Median = 4, Mode = 4'},
                {'problem': 'Data: 1, 3, 5, 7, 9, 11', 'solution': 'Mean = 36/6 = 6, Median = (5+7)/2 = 6, No mode'},
                {'problem': 'Data: 5, 5, 5, 10, 10, 15', 'solution': 'Mean = 50/6 ≈ 8.33, Median = (5+10)/2 = 7.5, Mode = 5'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Measures of Central Tendency</text><rect x="20" y="60" width="110" height="80" rx="8" fill="#667eea" opacity="0.2"/><text x="75" y="90" font-size="14" fill="#333" text-anchor="middle">Mean</text><text x="75" y="115" font-size="11" fill="#666" text-anchor="middle">Sum / Count</text><rect x="145" y="60" width="110" height="80" rx="8" fill="#764ba2" opacity="0.2"/><text x="200" y="90" font-size="14" fill="#333" text-anchor="middle">Median</text><text x="200" y="115" font-size="11" fill="#666" text-anchor="middle">Middle Value</text><rect x="270" y="60" width="110" height="80" rx="8" fill="#667eea" opacity="0.2"/><text x="325" y="90" font-size="14" fill="#333" text-anchor="middle">Mode</text><text x="325" y="115" font-size="11" fill="#666" text-anchor="middle">Most Frequent</text><path d="M 40 200 L 80 180 L 120 190 L 160 160 L 200 170 L 240 150 L 280 165 L 320 140 L 360 155" fill="none" stroke="#667eea" stroke-width="2"/><line x1="40" y1="220" x2="360" y2="220" stroke="#333" stroke-width="1"/><text x="200" y="260" font-size="12" fill="#666" text-anchor="middle">Data distribution with mean, median, mode marked</text></svg>',
            'types': [
                {'name': 'Arithmetic Mean', 'formula': 'x̄ = Σxᵢ/n', 'description': 'Sum divided by count'},
                {'name': 'Weighted Mean', 'formula': 'x̄ = Σ(wᵢxᵢ)/Σwᵢ', 'description': 'Each value has a weight'},
                {'name': 'Geometric Mean', 'formula': 'GM = (Πxᵢ)^(1/n)', 'description': 'nth root of product'},
                {'name': 'Harmonic Mean', 'formula': 'HM = n/Σ(1/xᵢ)', 'description': 'Reciprocal of arithmetic mean of reciprocals'}
            ],
            'formulas': [
                {'name': 'Mean', 'formula': 'x̄ = (x₁ + x₂ + ... + xₙ)/n'},
                {'name': 'Median (odd n)', 'formula': 'Middle value after sorting'},
                {'name': 'Median (even n)', 'formula': 'Average of two middle values'},
                {'name': 'Mode', 'formula': 'Most frequent value(s)'}
            ],
            'solved_problems': [
                {'problem': 'Find mean, median, mode: 3, 7, 7, 9, 14', 'steps': ['Mean = (3+7+7+9+14)/5 = 40/5 = 8', 'Median = 7 (middle value)', 'Mode = 7 (appears twice)'], 'answer': 'Mean=8, Median=7, Mode=7'},
                {'problem': 'Find median: 12, 5, 8, 3, 9, 15', 'steps': ['Sort: 3, 5, 8, 9, 12, 15', 'Even count: average of 3rd and 4th', '(8+9)/2 = 8.5'], 'answer': '8.5'},
                {'problem': 'Find mean of: 10, 20, 30, 40, 50', 'steps': ['Sum = 150', 'Count = 5', 'Mean = 150/5 = 30'], 'answer': '30'},
                {'problem': 'Data: 2, 2, 3, 4, 4, 4, 5, 6. Find all measures.', 'steps': ['Mean = 30/8 = 3.75', 'Median = (4+4)/2 = 4', 'Mode = 4 (appears 3 times)'], 'answer': 'Mean=3.75, Median=4, Mode=4'},
                {'problem': 'If mean of 5, 8, x, 12, 15 is 10, find x', 'steps': ['(5+8+x+12+15)/5 = 10', '40+x = 50', 'x = 10'], 'answer': 'x = 10'}
            ]
        },
        'Standard Deviation': {
            'definition': 'Standard deviation measures the spread or dispersion of data around the mean. A low SD means data is clustered near the mean; high SD means data is spread out.',
            'explanation': 'Standard deviation is the square root of variance. It is the most commonly used measure of variability and is essential for understanding data distribution.',
            'examples': [
                {'problem': 'Data: 2, 4, 4, 4, 5, 5, 7, 9', 'solution': 'Mean=5, Variance=4, SD=2'},
                {'problem': 'Data: 10, 10, 10, 10', 'solution': 'Mean=10, Variance=0, SD=0 (no spread)'},
                {'problem': 'Data: 1, 5, 9, 13', 'solution': 'Mean=7, Variance=20, SD≈4.47'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Normal Distribution</text><path d="M 50 250 Q 100 250 150 200 Q 200 50 250 200 Q 300 250 350 250" fill="none" stroke="#667eea" stroke-width="3"/><line x1="200" y1="50" x2="200" y2="250" stroke="#ff4757" stroke-width="2" stroke-dasharray="5,5"/><text x="200" y="270" font-size="12" fill="#ff4757" text-anchor="middle">μ (mean)</text><line x1="140" y1="150" x2="140" y2="250" stroke="#764ba2" stroke-width="1" stroke-dasharray="3,3"/><line x1="260" y1="150" x2="260" y2="250" stroke="#764ba2" stroke-width="1" stroke-dasharray="3,3"/><text x="140" y="265" font-size="11" fill="#764ba2" text-anchor="middle">μ-σ</text><text x="260" y="265" font-size="11" fill="#764ba2" text-anchor="middle">μ+σ</text><text x="200" y="290" font-size="12" fill="#666" text-anchor="middle">68% of data within ±1σ</text></svg>',
            'types': [
                {'name': 'Population SD', 'formula': 'σ = √(Σ(xᵢ-μ)²/N)', 'description': 'For entire population'},
                {'name': 'Sample SD', 'formula': 's = √(Σ(xᵢ-x̄)²/(n-1))', 'description': 'For sample data (Bessel correction)'},
                {'name': 'Variance', 'formula': 'σ² or s²', 'description': 'Square of standard deviation'},
                {'name': 'Coefficient of Variation', 'formula': 'CV = (σ/μ) × 100%', 'description': 'Relative variability'}
            ],
            'formulas': [
                {'name': 'Population SD', 'formula': 'σ = √(Σ(xᵢ-μ)²/N)'},
                {'name': 'Sample SD', 'formula': 's = √(Σ(xᵢ-x̄)²/(n-1))'},
                {'name': 'Variance', 'formula': 'σ² = Σ(xᵢ-μ)²/N'},
                {'name': 'Z-Score', 'formula': 'z = (x - μ)/σ'}
            ],
            'solved_problems': [
                {'problem': 'Find SD of: 4, 8, 6, 5, 7', 'steps': ['Mean = 30/5 = 6', 'Deviations: -2, 2, 0, -1, 1', 'Squared: 4, 4, 0, 1, 1', 'Variance = 10/5 = 2, SD = √2 ≈ 1.41'], 'answer': 'σ ≈ 1.41'},
                {'problem': 'Find sample SD: 3, 7, 7, 11, 12', 'steps': ['Mean = 40/5 = 8', 'Squared deviations: 25, 1, 1, 9, 16', 'Sum = 52', 's² = 52/4 = 13, s = √13 ≈ 3.61'], 'answer': 's ≈ 3.61'},
                {'problem': 'If μ=50, σ=10, find z-score for x=65', 'steps': ['z = (x - μ)/σ', 'z = (65 - 50)/10', 'z = 1.5'], 'answer': 'z = 1.5'},
                {'problem': 'Which is more variable: A(μ=100, σ=15) or B(μ=50, σ=10)?', 'steps': ['CV(A) = 15/100 × 100% = 15%', 'CV(B) = 10/50 × 100% = 20%', 'B has higher relative variability'], 'answer': 'B is more variable (CV=20% vs 15%)'},
                {'problem': 'Data: 2, 4, 6, 8, 10. Find variance and SD.', 'steps': ['Mean = 30/5 = 6', 'Squared deviations: 16, 4, 0, 4, 16', 'Sum = 40', 'σ² = 40/5 = 8, σ = √8 ≈ 2.83'], 'answer': 'Variance=8, SD≈2.83'}
            ]
        },
        'Probability Distributions': {
            'definition': 'A probability distribution describes how probabilities are distributed over the values of a random variable. It can be discrete or continuous.',
            'explanation': 'Common distributions include binomial (counting successes), normal (bell curve), Poisson (rare events), and uniform (equal likelihood). Each has specific applications.',
            'examples': [
                {'problem': 'Binomial: n=10, p=0.5, find P(X=6)', 'solution': 'C(10,6) × 0.5⁶ × 0.5⁴ = 210 × 0.000977 ≈ 0.205'},
                {'problem': 'Normal: μ=100, σ=15, find P(X<115)', 'solution': 'z = 1, P(Z<1) ≈ 0.8413'},
                {'problem': 'Poisson: λ=3, find P(X=2)', 'solution': 'P(X=2) = e⁻³ × 3²/2! ≈ 0.224'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Normal Distribution Bell Curve</text><path d="M 50 250 Q 100 250 130 230 Q 160 180 200 60 Q 240 180 270 230 Q 300 250 350 250" fill="#667eea" opacity="0.2" stroke="#667eea" stroke-width="2"/><line x1="200" y1="60" x2="200" y2="250" stroke="#ff4757" stroke-width="2"/><text x="200" y="270" font-size="12" fill="#333" text-anchor="middle">μ</text><text x="130" y="265" font-size="11" fill="#666" text-anchor="middle">μ-σ</text><text x="270" y="265" font-size="11" fill="#666" text-anchor="middle">μ+σ</text><text x="200" y="290" font-size="12" fill="#666" text-anchor="middle">68-95-99.7 Rule</text></svg>',
            'types': [
                {'name': 'Binomial', 'formula': 'P(X=k) = C(n,k)pᵏ(1-p)ⁿ⁻ᵏ', 'description': 'Number of successes in n trials'},
                {'name': 'Normal', 'formula': 'f(x) = (1/σ√2π)e^(-(x-μ)²/2σ²)', 'description': 'Bell-shaped continuous distribution'},
                {'name': 'Poisson', 'formula': 'P(X=k) = e⁻λλᵏ/k!', 'description': 'Events in fixed interval'},
                {'name': 'Uniform', 'formula': 'P(X=x) = 1/(b-a)', 'description': 'Equal probability for all outcomes'}
            ],
            'formulas': [
                {'name': 'Binomial', 'formula': 'P(X=k) = C(n,k)pᵏ(1-p)ⁿ⁻ᵏ'},
                {'name': 'Expected Value', 'formula': 'E(X) = ΣxᵢP(xᵢ)'},
                {'name': 'Normal Z-Score', 'formula': 'z = (x - μ)/σ'},
                {'name': 'Poisson', 'formula': 'P(X=k) = e⁻λλᵏ/k!'}
            ],
            'solved_problems': [
                {'problem': 'Coin flipped 5 times. P(exactly 3 heads)?', 'steps': ['n=5, p=0.5, k=3', 'P(X=3) = C(5,3) × 0.5³ × 0.5²', 'P = 10 × 0.125 × 0.25 = 0.3125'], 'answer': '0.3125 or 31.25%'},
                {'problem': 'Test scores: μ=75, σ=10. P(score > 85)?', 'steps': ['z = (85-75)/10 = 1', 'P(Z > 1) = 1 - 0.8413', 'P = 0.1587'], 'answer': '≈ 15.87%'},
                {'problem': 'Average 2 customers/hour. P(3 customers)?', 'steps': ['Poisson with λ=2, k=3', 'P(X=3) = e⁻² × 2³/3!', 'P = 0.1353 × 8/6 ≈ 0.1804'], 'answer': '≈ 18.04%'},
                {'problem': 'Find E(X) for die roll', 'steps': ['E(X) = (1+2+3+4+5+6)/6', 'E(X) = 21/6 = 3.5'], 'answer': '3.5'},
                {'problem': 'P(-1 < Z < 1) for standard normal', 'steps': ['P(Z < 1) = 0.8413', 'P(Z < -1) = 0.1587', 'P = 0.8413 - 0.1587 = 0.6826'], 'answer': '≈ 68.26%'}
            ]
        },
        'Hypothesis Testing': {
            'definition': 'Hypothesis testing is a statistical method for making decisions about population parameters based on sample data. It involves testing a null hypothesis against an alternative.',
            'explanation': 'The process involves stating hypotheses, choosing significance level, calculating test statistic, finding p-value, and making a decision. Type I error rejects true H₀; Type II error fails to reject false H₀.',
            'examples': [
                {'problem': 'Test if mean ≠ 100, sample: x̄=105, n=30, σ=15', 'solution': 'z = (105-100)/(15/√30) = 1.83, p-value ≈ 0.067'},
                {'problem': 'Test if proportion > 0.5, 60/100 successes', 'solution': 'z = (0.6-0.5)/√(0.5×0.5/100) = 2, p-value ≈ 0.023'},
                {'problem': 'α=0.05, p-value=0.03', 'solution': 'Since p < α, reject H₀'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Hypothesis Testing Decision</text><path d="M 50 250 Q 100 250 130 230 Q 160 180 200 60 Q 240 180 270 230 Q 300 250 350 250" fill="none" stroke="#667eea" stroke-width="2"/><line x1="280" y1="100" x2="280" y2="250" stroke="#ff4757" stroke-width="2"/><path d="M 280 100 Q 300 180 350 250 L 350 250 L 280 250 Z" fill="#ff4757" opacity="0.2"/><text x="310" y="200" font-size="12" fill="#ff4757">Reject H₀</text><text x="200" y="270" font-size="12" fill="#666" text-anchor="middle">α = 0.05 (rejection region)</text></svg>',
            'types': [
                {'name': 'Z-Test', 'formula': 'z = (x̄ - μ)/(σ/√n)', 'description': 'Large sample, known σ'},
                {'name': 'T-Test', 'formula': 't = (x̄ - μ)/(s/√n)', 'description': 'Small sample, unknown σ'},
                {'name': 'Chi-Square', 'formula': 'χ² = Σ(O-E)²/E', 'description': 'Goodness of fit, independence'},
                {'name': 'Proportion Test', 'formula': 'z = (p̂ - p₀)/√(p₀(1-p₀)/n)', 'description': 'Testing proportions'}
            ],
            'formulas': [
                {'name': 'Z-Statistic', 'formula': 'z = (x̄ - μ)/(σ/√n)'},
                {'name': 'T-Statistic', 'formula': 't = (x̄ - μ)/(s/√n)'},
                {'name': 'P-Value', 'formula': 'Probability of observed result if H₀ true'},
                {'name': 'Confidence Interval', 'formula': 'x̄ ± z(α/2) × σ/√n'}
            ],
            'solved_problems': [
                {'problem': 'Test H₀: μ=50 vs H₁: μ≠50, x̄=53, n=36, σ=12, α=0.05', 'steps': ['z = (53-50)/(12/6) = 3/2 = 1.5', 'Critical z = ±1.96 for α=0.05', '|1.5| < 1.96, fail to reject H₀'], 'answer': 'Fail to reject H₀ (insufficient evidence)'},
                {'problem': 'Test H₀: p=0.4 vs H₁: p>0.4, 55/100, α=0.05', 'steps': ['p̂ = 0.55', 'z = (0.55-0.4)/√(0.4×0.6/100) = 0.15/0.049 = 3.06', 'Critical z = 1.645 for one-tailed', '3.06 > 1.645, reject H₀'], 'answer': 'Reject H₀ (p > 0.4)'},
                {'problem': 'Find 95% CI: x̄=80, σ=10, n=25', 'steps': ['z(0.025) = 1.96', 'Margin = 1.96 × 10/5 = 3.92', 'CI = 80 ± 3.92 = (76.08, 83.92)'], 'answer': '(76.08, 83.92)'},
                {'problem': 't-test: x̄=45, μ=40, s=8, n=16, α=0.05', 'steps': ['t = (45-40)/(8/4) = 5/2 = 2.5', 'df = 15, critical t = 2.131', '2.5 > 2.131, reject H₀'], 'answer': 'Reject H₀ (significant difference)'},
                {'problem': 'Interpret p-value = 0.02 at α = 0.05', 'steps': ['p-value = 0.02 < α = 0.05', 'Result is statistically significant', 'Reject the null hypothesis'], 'answer': 'Reject H₀, result is significant'}
            ]
        },
        'Regression Analysis': {
            'definition': 'Regression analysis models the relationship between a dependent variable and one or more independent variables. Simple linear regression fits a line to data points.',
            'explanation': 'The least squares method finds the line that minimizes the sum of squared residuals. The correlation coefficient r measures the strength and direction of linear relationship.',
            'examples': [
                {'problem': 'Data: (1,2), (2,4), (3,5), (4,4), (5,5)', 'solution': 'Regression line: y = 0.7x + 2.1'},
                {'problem': 'r = 0.95', 'solution': 'Strong positive linear relationship'},
                {'problem': 'Predict y when x=6, line: y=2x+3', 'solution': 'y = 2(6)+3 = 15'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Linear Regression</text><line x1="50" y1="250" x2="350" y2="50" stroke="#667eea" stroke-width="2"/><circle cx="100" cy="200" r="5" fill="#764ba2"/><circle cx="150" cy="170" r="5" fill="#764ba2"/><circle cx="200" cy="150" r="5" fill="#764ba2"/><circle cx="250" cy="120" r="5" fill="#764ba2"/><circle cx="300" cy="100" r="5" fill="#764ba2"/><circle cx="120" cy="180" r="5" fill="#ff4757"/><circle cx="180" cy="160" r="5" fill="#ff4757"/><circle cx="280" cy="110" r="5" fill="#ff4757"/><text x="200" y="280" font-size="12" fill="#666" text-anchor="middle">y = mx + b (best fit line)</text></svg>',
            'types': [
                {'name': 'Simple Linear', 'formula': 'y = mx + b', 'description': 'One independent variable'},
                {'name': 'Multiple Linear', 'formula': 'y = b₀ + b₁x₁ + b₂x₂ + ...', 'description': 'Multiple independent variables'},
                {'name': 'Polynomial', 'formula': 'y = a₀ + a₁x + a₂x² + ...', 'description': 'Curved relationship'},
                {'name': 'Logistic', 'formula': 'P = 1/(1+e^(-z))', 'description': 'Binary outcome prediction'}
            ],
            'formulas': [
                {'name': 'Slope', 'formula': 'm = (nΣxy - ΣxΣy)/(nΣx² - (Σx)²)'},
                {'name': 'Intercept', 'formula': 'b = (Σy - mΣx)/n'},
                {'name': 'Correlation', 'formula': 'r = (nΣxy - ΣxΣy)/√((nΣx²-(Σx)²)(nΣy²-(Σy)²))'},
                {'name': 'R-Squared', 'formula': 'R² = r² (coefficient of determination)'}
            ],
            'solved_problems': [
                {'problem': 'Find regression line for: (1,3), (2,5), (3,7)', 'steps': ['Σx=6, Σy=15, Σxy=44, Σx²=14, n=3', 'm = (3×44-6×15)/(3×14-36) = 42/6 = 7', 'b = (15-7×6)/3 = -9', 'y = 7x - 9... wait, check: m=(132-90)/(42-36)=42/6=7'], 'answer': 'y = 2x + 1 (perfect linear relationship)'},
                {'problem': 'Interpret r = -0.85', 'steps': ['Negative: inverse relationship', '|r| = 0.85: strong correlation', 'r² = 0.7225: 72.25% of variation explained'], 'answer': 'Strong negative linear relationship'},
                {'problem': 'Predict y when x=10, line: y=3x+5', 'steps': ['y = 3(10) + 5', 'y = 35'], 'answer': 'y = 35'},
                {'problem': 'Find r for: (1,2), (2,3), (3,5), (4,4)', 'steps': ['Σx=10, Σy=14, Σxy=43, Σx²=30, Σy²=54, n=4', 'r = (4×43-10×14)/√((4×30-100)(4×54-196))', 'r = 32/√(20×20) = 32/20 = 0.8'], 'answer': 'r = 0.8 (strong positive)'},
                {'problem': 'If R² = 0.64, what does it mean?', 'steps': ['R² = 0.64 means 64% of variation in y', 'is explained by the regression model', '36% is due to other factors'], 'answer': '64% of variation explained by model'}
            ]
        }
    },
    'Number Theory': {
        'Prime Numbers': {
            'definition': 'A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself. Prime numbers are the building blocks of all natural numbers.',
            'explanation': 'Every natural number greater than 1 can be uniquely expressed as a product of primes (Fundamental Theorem of Arithmetic). Primes are essential in cryptography and number theory.',
            'examples': [
                {'problem': 'Is 17 prime?', 'solution': 'Yes, 17 is only divisible by 1 and 17'},
                {'problem': 'Is 21 prime?', 'solution': 'No, 21 = 3 × 7'},
                {'problem': 'List primes up to 20', 'solution': '2, 3, 5, 7, 11, 13, 17, 19'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Sieve of Eratosthenes</text><text x="200" y="270" font-size="12" fill="#666" text-anchor="middle">Primes up to 30: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29</text></svg>',
            'types': [
                {'name': 'Twin Primes', 'formula': '(p, p+2) both prime', 'description': 'Pairs differing by 2'},
                {'name': 'Mersenne Primes', 'formula': '2ᵖ - 1 where p is prime', 'description': 'Special form primes'},
                {'name': 'Fermat Primes', 'formula': '2^(2ⁿ) + 1', 'description': 'Fermat number primes'},
                {'name': 'Sophie Germain', 'formula': 'p where 2p+1 is also prime', 'description': 'Special prime pairs'}
            ],
            'formulas': [
                {'name': 'Prime Counting', 'formula': 'π(x) ≈ x/ln(x)'},
                {'name': 'Fundamental Theorem', 'formula': 'n = p₁^a₁ × p₂^a₂ × ... × pₖ^aₖ'},
                {'name': 'Sieve Method', 'formula': 'Eliminate multiples systematically'},
                {'name': 'Primality Test', 'formula': 'Check divisibility up to √n'}
            ],
            'solved_problems': [
                {'problem': 'Is 97 prime?', 'steps': ['Check divisibility up to √97 ≈ 9.8', 'Test: 2, 3, 5, 7', '97 is not divisible by any', '97 is prime'], 'answer': 'Yes, 97 is prime'},
                {'problem': 'Find prime factorization of 60', 'steps': ['60 = 2 × 30', '30 = 2 × 15', '15 = 3 × 5', '60 = 2² × 3 × 5'], 'answer': '60 = 2² × 3 × 5'},
                {'problem': 'How many primes between 1 and 50?', 'steps': ['List: 2, 3, 5, 7, 11, 13, 17, 19', 'Continue: 23, 29, 31, 37, 41, 43, 47', 'Count: 15 primes'], 'answer': '15 primes'},
                {'problem': 'Find smallest prime factor of 143', 'steps': ['√143 ≈ 11.96', 'Test: 2 (no), 3 (no), 5 (no)', '7: 143/7 = 20.4 (no)', '11: 143/11 = 13 (yes!)'], 'answer': '11'},
                {'problem': 'Prove there are infinitely many primes', 'steps': ['Assume finite: p₁, p₂, ..., pₙ', 'Consider N = p₁p₂...pₙ + 1', 'N is not divisible by any pᵢ', 'Contradiction: N is prime or has new prime factor'], 'answer': 'Proof by contradiction (Euclid)'}
            ]
        },
        'Divisibility': {
            'definition': 'Divisibility refers to whether one integer can be divided by another without leaving a remainder. If a divides b evenly, we write a|b.',
            'explanation': 'Divisibility rules help quickly determine if a number is divisible by another without performing full division. These rules are based on properties of the base-10 system.',
            'examples': [
                {'problem': 'Is 123456 divisible by 3?', 'solution': 'Sum of digits: 1+2+3+4+5+6=21, 21÷3=7, Yes!'},
                {'problem': 'Is 5678 divisible by 4?', 'solution': 'Last two digits: 78, 78÷4=19.5, No'},
                {'problem': 'Is 123456789 divisible by 9?', 'solution': 'Sum: 45, 45÷9=5, Yes!'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Divisibility Rules</text><rect x="20" y="60" width="170" height="40" rx="8" fill="#667eea" opacity="0.2"/><text x="105" y="85" font-size="13" fill="#333" text-anchor="middle">By 2: Last digit even</text><rect x="210" y="60" width="170" height="40" rx="8" fill="#764ba2" opacity="0.2"/><text x="295" y="85" font-size="13" fill="#333" text-anchor="middle">By 3: Sum of digits</text><rect x="20" y="110" width="170" height="40" rx="8" fill="#667eea" opacity="0.2"/><text x="105" y="135" font-size="13" fill="#333" text-anchor="middle">By 5: Ends in 0 or 5</text><rect x="210" y="110" width="170" height="40" rx="8" fill="#764ba2" opacity="0.2"/><text x="295" y="135" font-size="13" fill="#333" text-anchor="middle">By 9: Sum divisible by 9</text><rect x="20" y="160" width="170" height="40" rx="8" fill="#667eea" opacity="0.2"/><text x="105" y="185" font-size="13" fill="#333" text-anchor="middle">By 4: Last 2 digits ÷ 4</text><rect x="210" y="160" width="170" height="40" rx="8" fill="#764ba2" opacity="0.2"/><text x="295" y="185" font-size="13" fill="#333" text-anchor="middle">By 11: Alt sum ÷ 11</text></svg>',
            'types': [
                {'name': 'Divisible by 2', 'formula': 'Last digit is 0, 2, 4, 6, or 8', 'description': 'Even numbers'},
                {'name': 'Divisible by 3', 'formula': 'Sum of digits divisible by 3', 'description': 'Digital root test'},
                {'name': 'Divisible by 5', 'formula': 'Last digit is 0 or 5', 'description': 'Ends in 0 or 5'},
                {'name': 'Divisible by 11', 'formula': 'Alternating sum divisible by 11', 'description': 'Add-subtract pattern'}
            ],
            'formulas': [
                {'name': 'Division Algorithm', 'formula': 'a = bq + r, 0 ≤ r < b'},
                {'name': 'Divisibility by 3', 'formula': '3|n iff 3|sum_of_digits(n)'},
                {'name': 'Divisibility by 11', 'formula': '11|n iff 11|alternating_sum(n)'},
                {'name': 'Transitivity', 'formula': 'If a|b and b|c, then a|c'}
            ],
            'solved_problems': [
                {'problem': 'Is 7854 divisible by 6?', 'steps': ['Check divisibility by 2: last digit 4, Yes', 'Check divisibility by 3: 7+8+5+4=24, 24÷3=8, Yes', 'Divisible by both 2 and 3, so by 6'], 'answer': 'Yes, 7854 ÷ 6 = 1309'},
                {'problem': 'Find remainder when 1234 is divided by 7', 'steps': ['1234 = 7 × 176 + 2', 'Or: 1234 - 7×176 = 1234 - 1232 = 2'], 'answer': 'Remainder = 2'},
                {'problem': 'Is 987654321 divisible by 9?', 'steps': ['Sum of digits: 9+8+7+6+5+4+3+2+1 = 45', '45 ÷ 9 = 5', 'Yes, divisible by 9'], 'answer': 'Yes'},
                {'problem': 'Find all divisors of 24', 'steps': ['24 = 2³ × 3', 'Divisors: 1, 2, 3, 4, 6, 8, 12, 24'], 'answer': '1, 2, 3, 4, 6, 8, 12, 24'},
                {'problem': 'If 5|n and 7|n, prove 35|n', 'steps': ['5|n means n = 5k for some k', '7|n means 7|5k', 'Since gcd(5,7)=1, 7|k', 'So k = 7m, n = 5×7m = 35m'], 'answer': '35|n (proved)'}
            ]
        },
        'GCD & LCM': {
            'definition': 'GCD (Greatest Common Divisor) is the largest number that divides two or more numbers. LCM (Least Common Multiple) is the smallest number that is a multiple of two or more numbers.',
            'explanation': 'GCD and LCM are fundamental concepts used in simplifying fractions, solving problems involving periodicity, and number theory. They are related by: GCD(a,b) × LCM(a,b) = a × b.',
            'examples': [
                {'problem': 'GCD(12, 18)', 'solution': '12 = 2²×3, 18 = 2×3², GCD = 2×3 = 6'},
                {'problem': 'LCM(4, 6)', 'solution': '4 = 2², 6 = 2×3, LCM = 2²×3 = 12'},
                {'problem': 'GCD(48, 60) using Euclidean', 'solution': '60 = 48×1 + 12, 48 = 12×4 + 0, GCD = 12'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">GCD & LCM Relationship</text><circle cx="150" cy="150" r="80" fill="#667eea" opacity="0.2" stroke="#667eea" stroke-width="2"/><circle cx="250" cy="150" r="80" fill="#764ba2" opacity="0.2" stroke="#764ba2" stroke-width="2"/><text x="120" y="155" font-size="14" fill="#667eea" text-anchor="middle">12</text><text x="280" y="155" font-size="14" fill="#764ba2" text-anchor="middle">18</text><text x="200" y="155" font-size="14" fill="#333" text-anchor="middle">GCD=6</text><text x="200" y="250" font-size="14" fill="#333" text-anchor="middle">LCM = 36</text><text x="200" y="280" font-size="12" fill="#666" text-anchor="middle">GCD × LCM = 12 × 18 = 216</text></svg>',
            'types': [
                {'name': 'Euclidean Algorithm', 'formula': 'GCD(a,b) = GCD(b, a mod b)', 'description': 'Efficient GCD computation'},
                {'name': 'Prime Factorization', 'formula': 'GCD: min powers, LCM: max powers', 'description': 'Using prime factors'},
                {'name': 'Extended Euclidean', 'formula': 'ax + by = GCD(a,b)', 'description': 'Finds coefficients x, y'},
                {'name': 'Multiple Numbers', 'formula': 'GCD(a,b,c) = GCD(GCD(a,b), c)', 'description': 'Iterative approach'}
            ],
            'formulas': [
                {'name': 'GCD-LCM Relation', 'formula': 'GCD(a,b) × LCM(a,b) = a × b'},
                {'name': 'Euclidean', 'formula': 'GCD(a,b) = GCD(b, a mod b)'},
                {'name': 'LCM from GCD', 'formula': 'LCM(a,b) = (a×b)/GCD(a,b)'},
                {'name': 'Bezout\'s Identity', 'formula': 'ax + by = GCD(a,b)'}
            ],
            'solved_problems': [
                {'problem': 'Find GCD(84, 36) using Euclidean algorithm', 'steps': ['84 = 36×2 + 12', '36 = 12×3 + 0', 'GCD = 12'], 'answer': 'GCD(84, 36) = 12'},
                {'problem': 'Find LCM(15, 20, 25)', 'steps': ['15 = 3×5, 20 = 2²×5, 25 = 5²', 'LCM = 2²×3×5² = 300'], 'answer': '300'},
                {'problem': 'Two lights flash every 6 and 8 seconds. When do they flash together?', 'steps': ['Find LCM(6, 8)', '6 = 2×3, 8 = 2³', 'LCM = 2³×3 = 24'], 'answer': 'Every 24 seconds'},
                {'problem': 'Find GCD(1071, 462)', 'steps': ['1071 = 462×2 + 147', '462 = 147×3 + 21', '147 = 21×7 + 0', 'GCD = 21'], 'answer': '21'},
                {'problem': 'Simplify fraction 84/36', 'steps': ['GCD(84, 36) = 12', '84÷12 = 7, 36÷12 = 3', '84/36 = 7/3'], 'answer': '7/3'}
            ]
        },
        'Modular Arithmetic': {
            'definition': 'Modular arithmetic is a system of arithmetic for integers where numbers "wrap around" after reaching a certain value (the modulus). It is often called clock arithmetic.',
            'explanation': 'In modular arithmetic, a ≡ b (mod n) means a and b have the same remainder when divided by n. This concept is fundamental in cryptography, computer science, and number theory.',
            'examples': [
                {'problem': '17 mod 5', 'solution': '17 = 5×3 + 2, so 17 ≡ 2 (mod 5)'},
                {'problem': '(23 + 47) mod 10', 'solution': '70 mod 10 = 0'},
                {'problem': '3⁴ mod 7', 'solution': '81 mod 7 = 4 (since 81 = 7×11 + 4)'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Clock Arithmetic (mod 12)</text><circle cx="200" cy="160" r="100" fill="none" stroke="#667eea" stroke-width="3"/><text x="200" y="75" font-size="14" fill="#333" text-anchor="middle">12</text><text x="285" y="115" font-size="14" fill="#333" text-anchor="middle">3</text><text x="200" y="255" font-size="14" fill="#333" text-anchor="middle">6</text><text x="115" y="115" font-size="14" fill="#333" text-anchor="middle">9</text><text x="200" y="280" font-size="12" fill="#666" text-anchor="middle">17 ≡ 5 (mod 12)</text></svg>',
            'types': [
                {'name': 'Addition', 'formula': '(a + b) mod n', 'description': 'Add then take remainder'},
                {'name': 'Multiplication', 'formula': '(a × b) mod n', 'description': 'Multiply then take remainder'},
                {'name': 'Exponentiation', 'formula': 'aᵇ mod n', 'description': 'Power then remainder'},
                {'name': 'Modular Inverse', 'formula': 'a⁻¹ mod n exists if gcd(a,n)=1', 'description': 'Multiplicative inverse'}
            ],
            'formulas': [
                {'name': 'Congruence', 'formula': 'a ≡ b (mod n) iff n|(a-b)'},
                {'name': 'Addition', 'formula': '(a + b) mod n = ((a mod n) + (b mod n)) mod n'},
                {'name': 'Fermat\'s Little Theorem', 'formula': 'aᵖ⁻¹ ≡ 1 (mod p) if p prime, gcd(a,p)=1'},
                {'name': 'Euler\'s Theorem', 'formula': 'a^φ(n) ≡ 1 (mod n) if gcd(a,n)=1'}
            ],
            'solved_problems': [
                {'problem': 'Find 23 mod 7', 'steps': ['23 = 7×3 + 2', 'Remainder is 2'], 'answer': '2'},
                {'problem': 'Compute (15 × 23) mod 11', 'steps': ['15 mod 11 = 4, 23 mod 11 = 1', '4 × 1 = 4', '4 mod 11 = 4'], 'answer': '4'},
                {'problem': 'Find 3¹⁰ mod 7', 'steps': ['By Fermat: 3⁶ ≡ 1 (mod 7)', '3¹⁰ = 3⁶ × 3⁴ ≡ 1 × 3⁴ (mod 7)', '3⁴ = 81, 81 mod 7 = 4'], 'answer': '4'},
                {'problem': 'Solve: 3x ≡ 7 (mod 11)', 'steps': ['Find inverse of 3 mod 11', '3 × 4 = 12 ≡ 1 (mod 11), so 3⁻¹ = 4', 'x ≡ 4 × 7 = 28 ≡ 6 (mod 11)'], 'answer': 'x ≡ 6 (mod 11)'},
                {'problem': 'What day is 100 days from Monday?', 'steps': ['100 mod 7 = 2', 'Monday + 2 days = Wednesday'], 'answer': 'Wednesday'}
            ]
        },
        'Fermat\'s Theorem': {
            'definition': 'Fermat\'s Little Theorem states that if p is prime and a is not divisible by p, then aᵖ⁻¹ ≡ 1 (mod p). This is a fundamental result in number theory.',
            'explanation': 'Fermat\'s Little Theorem has applications in primality testing and cryptography (RSA). It provides a way to simplify large exponent calculations modulo a prime.',
            'examples': [
                {'problem': 'Verify for a=3, p=7', 'solution': '3⁶ = 729, 729 mod 7 = 1 ✓'},
                {'problem': 'Find 2¹⁰ mod 11', 'solution': 'By FLT: 2¹⁰ ≡ 1 (mod 11)'},
                {'problem': 'Find 5²⁰ mod 23', 'solution': 'By FLT: 5²² ≡ 1, so 5²⁰ = 5²²/5² ≡ 1/25 ≡ 1/2 ≡ 12 (mod 23)'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Fermat\'s Little Theorem</text><rect x="40" y="60" width="320" height="60" rx="8" fill="#667eea" opacity="0.15"/><text x="200" y="85" font-size="16" fill="#333" text-anchor="middle">aᵖ⁻¹ ≡ 1 (mod p)</text><text x="200" y="110" font-size="12" fill="#666" text-anchor="middle">if p is prime and gcd(a,p) = 1</text><rect x="40" y="140" width="320" height="50" rx="8" fill="#764ba2" opacity="0.15"/><text x="200" y="160" font-size="14" fill="#333" text-anchor="middle">Example: 3⁶ = 729 ≡ 1 (mod 7)</text><rect x="40" y="200" width="320" height="50" rx="8" fill="#667eea" opacity="0.15"/><text x="200" y="220" font-size="14" fill="#333" text-anchor="middle">Application: RSA Cryptography</text><text x="200" y="270" font-size="12" fill="#666" text-anchor="middle">Foundation of modern encryption</text></svg>',
            'types': [
                {'name': 'Fermat\'s Little Theorem', 'formula': 'aᵖ⁻¹ ≡ 1 (mod p)', 'description': 'For prime p, gcd(a,p)=1'},
                {'name': 'Euler\'s Theorem', 'formula': 'a^φ(n) ≡ 1 (mod n)', 'description': 'Generalization for composite n'},
                {'name': 'Fermat Primality Test', 'formula': 'If aⁿ⁻¹ ≢ 1 (mod n), n is composite', 'description': 'Probabilistic primality test'},
                {'name': 'Wilson\'s Theorem', 'formula': '(p-1)! ≡ -1 (mod p)', 'description': 'Characterizes primes'}
            ],
            'formulas': [
                {'name': 'Fermat\'s Little Theorem', 'formula': 'aᵖ⁻¹ ≡ 1 (mod p)'},
                {'name': 'Alternative Form', 'formula': 'aᵖ ≡ a (mod p) for all a'},
                {'name': 'Modular Inverse', 'formula': 'a⁻¹ ≡ aᵖ⁻² (mod p)'},
                {'name': 'Euler\'s Theorem', 'formula': 'a^φ(n) ≡ 1 (mod n)'}
            ],
            'solved_problems': [
                {'problem': 'Verify FLT for a=2, p=5', 'steps': ['2⁴ = 16', '16 mod 5 = 1', 'Verified: 2⁴ ≡ 1 (mod 5)'], 'answer': '2⁴ ≡ 1 (mod 5) ✓'},
                {'problem': 'Find 7¹⁰ mod 11', 'steps': ['By FLT: 7¹⁰ ≡ 1 (mod 11)', 'Since 11 is prime and gcd(7,11)=1'], 'answer': '1'},
                {'problem': 'Find modular inverse of 3 mod 13', 'steps': ['By FLT: 3⁻¹ ≡ 3¹¹ (mod 13)', '3² = 9, 3⁴ = 81 ≡ 3 (mod 13)', '3⁸ ≡ 9, 3¹¹ = 3⁸ × 3² × 3 ≡ 9×9×3 = 243', '243 mod 13 = 9'], 'answer': '3⁻¹ ≡ 9 (mod 13)'},
                {'problem': 'Use FLT to find 4⁵⁰ mod 17', 'steps': ['By FLT: 4¹⁶ ≡ 1 (mod 17)', '50 = 16×3 + 2', '4⁵⁰ = (4¹⁶)³ × 4² ≡ 1 × 16 = 16'], 'answer': '16'},
                {'problem': 'Show 341 is not prime using FLT', 'steps': ['If 341 were prime, 2³⁴⁰ ≡ 1 (mod 341)', 'But 2³⁴⁰ mod 341 ≠ 1', '341 = 11 × 31 (composite)'], 'answer': '341 is composite (11 × 31)'}
            ]
        }
    },
    'Linear Algebra': {
        'Matrices & Determinants': {
            'definition': 'A matrix is a rectangular array of numbers arranged in rows and columns. A determinant is a scalar value computed from a square matrix that encodes certain properties.',
            'explanation': 'Matrices are fundamental in linear algebra, used to represent linear transformations, solve systems of equations, and model real-world problems. Determinants help determine if a matrix is invertible.',
            'examples': [
                {'problem': '2×2 matrix: [[1,2],[3,4]]', 'solution': 'Determinant = 1×4 - 2×3 = -2'},
                {'problem': 'Add [[1,2],[3,4]] + [[5,6],[7,8]]', 'solution': '[[6,8],[10,12]]'},
                {'problem': 'Multiply [[1,2],[3,4]] × [[2,0],[1,3]]', 'solution': '[[4,6],[10,12]]'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">2×2 Matrix</text><rect x="120" y="60" width="160" height="80" fill="#667eea" opacity="0.2" stroke="#667eea" stroke-width="2"/><text x="160" y="95" font-size="16" fill="#333" text-anchor="middle">1  2</text><text x="160" y="125" font-size="16" fill="#333" text-anchor="middle">3  4</text><text x="200" y="180" font-size="14" fill="#333" text-anchor="middle">det = ad - bc = -2</text><text x="200" y="210" font-size="12" fill="#666" text-anchor="middle">Rows: 2, Columns: 2</text><text x="200" y="250" font-size="12" fill="#666" text-anchor="middle">Square matrices have determinants</text></svg>',
            'types': [
                {'name': 'Square Matrix', 'formula': 'n × n matrix', 'description': 'Same number of rows and columns'},
                {'name': 'Identity Matrix', 'formula': 'I = [[1,0],[0,1]]', 'description': 'Diagonal elements are 1'},
                {'name': 'Zero Matrix', 'formula': 'All elements are 0', 'description': 'Additive identity'},
                {'name': 'Diagonal Matrix', 'formula': 'Non-zero only on diagonal', 'description': 'Off-diagonal elements are 0'}
            ],
            'formulas': [
                {'name': '2×2 Determinant', 'formula': 'det = ad - bc'},
                {'name': '3×3 Determinant', 'formula': 'a(ei-fh) - b(di-fg) + c(dh-eg)'},
                {'name': 'Matrix Addition', 'formula': '(A+B)ᵢⱼ = Aᵢⱼ + Bᵢⱼ'},
                {'name': 'Matrix Multiplication', 'formula': '(AB)ᵢⱼ = Σₖ AᵢₖBₖⱼ'}
            ],
            'solved_problems': [
                {'problem': 'Find determinant of [[3,1],[2,4]]', 'steps': ['det = 3×4 - 1×2', 'det = 12 - 2 = 10'], 'answer': '10'},
                {'problem': 'Multiply [[1,2],[3,4]] × [[5,6],[7,8]]', 'steps': ['Row 1: 1×5+2×7=19, 1×6+2×8=22', 'Row 2: 3×5+4×7=43, 3×6+4×8=50'], 'answer': '[[19,22],[43,50]]'},
                {'problem': 'Find inverse of [[2,1],[5,3]]', 'steps': ['det = 6-5 = 1', 'Inverse = (1/det) × [[3,-1],[-5,2]]', 'Inverse = [[3,-1],[-5,2]]'], 'answer': '[[3,-1],[-5,2]]'},
                {'problem': 'Solve using Cramer\'s rule: 2x+y=5, x+3y=7', 'steps': ['D = 6-1 = 5', 'Dₓ = 15-7 = 8, x = 8/5', 'Dᵧ = 14-5 = 9, y = 9/5'], 'answer': 'x = 8/5, y = 9/5'},
                {'problem': 'Find trace of [[1,2,3],[4,5,6],[7,8,9]]', 'steps': ['Trace = sum of diagonal elements', 'Trace = 1 + 5 + 9 = 15'], 'answer': '15'}
            ]
        },
        'Vector Spaces': {
            'definition': 'A vector space is a collection of vectors that can be added together and multiplied by scalars, satisfying specific axioms. It is the fundamental structure in linear algebra.',
            'explanation': 'Vector spaces generalize the notion of Euclidean space. They include Rⁿ, function spaces, polynomial spaces, and more. Key concepts include basis, dimension, and subspaces.',
            'examples': [
                {'problem': 'R² is a vector space', 'solution': 'All 2D vectors with standard addition and scalar multiplication'},
                {'problem': 'Check if (1,2,3) and (4,5,6) span R³', 'solution': 'No, need 3 linearly independent vectors for R³'},
                {'problem': 'Find dimension of P₂ (polynomials degree ≤ 2)', 'solution': 'Basis: {1, x, x²}, dimension = 3'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Vector in R²</text><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><line x1="200" y1="250" x2="280" y2="150" stroke="#667eea" stroke-width="3"/><polygon points="280,150 270,160 275,155" fill="#667eea"/><text x="290" y="145" font-size="12" fill="#667eea">v⃗ = (3, 4)</text><text x="200" y="270" font-size="12" fill="#666" text-anchor="middle">Vectors have magnitude and direction</text></svg>',
            'types': [
                {'name': 'Euclidean Space', 'formula': 'Rⁿ', 'description': 'n-dimensional real space'},
                {'name': 'Subspace', 'formula': 'W ⊆ V closed under + and ×', 'description': 'Subset that is itself a vector space'},
                {'name': 'Basis', 'formula': 'Linearly independent spanning set', 'description': 'Minimal generating set'},
                {'name': 'Dimension', 'formula': 'Number of basis vectors', 'description': 'Size of the space'}
            ],
            'formulas': [
                {'name': 'Vector Addition', 'formula': '(a₁,...,aₙ) + (b₁,...,bₙ) = (a₁+b₁,...,aₙ+bₙ)'},
                {'name': 'Scalar Multiplication', 'formula': 'c(a₁,...,aₙ) = (ca₁,...,caₙ)'},
                {'name': 'Dot Product', 'formula': 'a·b = Σaᵢbᵢ'},
                {'name': 'Norm', 'formula': '||v|| = √(v·v)'}
            ],
            'solved_problems': [
                {'problem': 'Check if (1,2) and (3,4) are linearly independent', 'steps': ['c₁(1,2) + c₂(3,4) = (0,0)', 'c₁ + 3c₂ = 0, 2c₁ + 4c₂ = 0', 'Solving: c₁ = c₂ = 0 only solution', 'Linearly independent'], 'answer': 'Yes, linearly independent'},
                {'problem': 'Find the span of (1,0) and (0,1)', 'steps': ['c₁(1,0) + c₂(0,1) = (c₁, c₂)', 'Any vector (a,b) in R² can be formed', 'Span = R²'], 'answer': 'Span = R²'},
                {'problem': 'Find dimension of subspace: {(x,y,z): x+y+z=0}', 'steps': ['One constraint on 3 variables', 'Dimension = 3 - 1 = 2', 'Basis: (1,-1,0), (1,0,-1)'], 'answer': 'Dimension = 2'},
                {'problem': 'Dot product of (1,2,3) and (4,5,6)', 'steps': ['1×4 + 2×5 + 3×6', '4 + 10 + 18 = 32'], 'answer': '32'},
                {'problem': 'Find norm of (3,4)', 'steps': ['||v|| = √(3² + 4²)', '||v|| = √(9 + 16) = √25 = 5'], 'answer': '5'}
            ]
        },
        'Eigenvalues': {
            'definition': 'An eigenvalue λ of a matrix A is a scalar such that Av = λv for some non-zero vector v (the eigenvector). Eigenvalues reveal important properties of linear transformations.',
            'explanation': 'Eigenvalues and eigenvectors are crucial in many applications: stability analysis, quantum mechanics, principal component analysis, and solving differential equations.',
            'examples': [
                {'problem': 'Find eigenvalues of [[2,0],[0,3]]', 'solution': 'Diagonal matrix: λ₁ = 2, λ₂ = 3'},
                {'problem': 'Find eigenvalues of [[4,1],[2,3]]', 'solution': 'det(A-λI) = (4-λ)(3-λ)-2 = λ²-7λ+10 = 0, λ = 2, 5'},
                {'problem': 'Trace = sum of eigenvalues', 'solution': 'For [[4,1],[2,3]]: trace = 7 = 2 + 5 ✓'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Eigenvector Transformation</text><line x1="200" y1="250" x2="200" y2="50" stroke="#667eea" stroke-width="3"/><polygon points="200,50 190,70 195,65" fill="#667eea"/><text x="210" y="60" font-size="12" fill="#667eea">v⃗</text><line x1="200" y1="250" x2="200" y2="20" stroke="#764ba2" stroke-width="2"/><polygon points="200,20 193,35 197,30" fill="#764ba2"/><text x="210" y="30" font-size="12" fill="#764ba2">Av⃗ = λv⃗</text><text x="200" y="280" font-size="12" fill="#666" text-anchor="middle">Eigenvector direction unchanged</text></svg>',
            'types': [
                {'name': 'Real Eigenvalues', 'formula': 'λ ∈ R', 'description': 'Standard eigenvalues'},
                {'name': 'Complex Eigenvalues', 'formula': 'λ = a + bi', 'description': 'Occurs in rotation matrices'},
                {'name': 'Repeated Eigenvalues', 'formula': 'Algebraic multiplicity > 1', 'description': 'Multiple roots of characteristic polynomial'},
                {'name': 'Spectral Theorem', 'formula': 'Symmetric matrices have real eigenvalues', 'description': 'Special property of symmetric matrices'}
            ],
            'formulas': [
                {'name': 'Characteristic Equation', 'formula': 'det(A - λI) = 0'},
                {'name': 'Eigenvalue Equation', 'formula': 'Av = λv'},
                {'name': 'Trace', 'formula': 'tr(A) = Σλᵢ'},
                {'name': 'Determinant', 'formula': 'det(A) = Πλᵢ'}
            ],
            'solved_problems': [
                {'problem': 'Find eigenvalues of [[3,1],[0,2]]', 'steps': ['det([[3-λ,1],[0,2-λ]]) = 0', '(3-λ)(2-λ) = 0', 'λ = 3 or λ = 2'], 'answer': 'λ₁ = 3, λ₂ = 2'},
                {'problem': 'Find eigenvector for λ=2 of [[3,1],[0,2]]', 'steps': ['(A-2I)v = 0', '[[1,1],[0,0]][x,y]ᵀ = [0,0]ᵀ', 'x + y = 0, so y = -x', 'v = (1, -1)'], 'answer': 'v = (1, -1)'},
                {'problem': 'Find eigenvalues of [[1,2],[2,1]]', 'steps': ['det([[1-λ,2],[2,1-λ]]) = 0', '(1-λ)² - 4 = 0', 'λ² - 2λ - 3 = 0', '(λ-3)(λ+1) = 0'], 'answer': 'λ₁ = 3, λ₂ = -1'},
                {'problem': 'Verify: trace = sum of eigenvalues for [[4,2],[1,3]]', 'steps': ['Trace = 4 + 3 = 7', 'det(A-λI) = (4-λ)(3-λ)-2 = λ²-7λ+10', 'λ = 2, 5', 'Sum = 2 + 5 = 7 = trace ✓'], 'answer': 'Verified: 7 = 7'},
                {'problem': 'Find eigenvalues of [[0,-1],[1,0]]', 'steps': ['det([[-λ,-1],[1,-λ]]) = λ² + 1 = 0', 'λ² = -1', 'λ = ±i'], 'answer': 'λ₁ = i, λ₂ = -i (complex)'}
            ]
        },
        'Linear Transformations': {
            'definition': 'A linear transformation T: V → W is a function between vector spaces that preserves vector addition and scalar multiplication: T(u+v) = T(u)+T(v) and T(cv) = cT(v).',
            'explanation': 'Linear transformations can be represented by matrices. They include rotations, reflections, projections, and scalings. Understanding them is key to applications in computer graphics, physics, and engineering.',
            'examples': [
                {'problem': 'T(x,y) = (2x, 3y)', 'solution': 'Scaling transformation: stretches x by 2, y by 3'},
                {'problem': 'Rotation by 90°: T(x,y) = (-y, x)', 'solution': 'Matrix: [[0,-1],[1,0]]'},
                {'problem': 'Projection onto x-axis: T(x,y) = (x, 0)', 'solution': 'Matrix: [[1,0],[0,0]]'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Linear Transformation</text><rect x="50" y="80" width="100" height="100" fill="#667eea" opacity="0.3" stroke="#667eea" stroke-width="2"/><text x="100" y="135" font-size="12" fill="#333" text-anchor="middle">Original</text><text x="180" y="135" font-size="24" fill="#333" text-anchor="middle">→</text><polygon points="230,80 330,100 310,180 210,160" fill="#764ba2" opacity="0.3" stroke="#764ba2" stroke-width="2"/><text x="270" y="135" font-size="12" fill="#333" text-anchor="middle">Transformed</text><text x="200" y="220" font-size="12" fill="#666" text-anchor="middle">T preserves lines and origin</text></svg>',
            'types': [
                {'name': 'Rotation', 'formula': '[[cos θ, -sin θ],[sin θ, cos θ]]', 'description': 'Rotates vectors by angle θ'},
                {'name': 'Reflection', 'formula': '[[1,0],[0,-1]] (over x-axis)', 'description': 'Flips vectors across a line'},
                {'name': 'Projection', 'formula': 'Projects onto subspace', 'description': 'Maps to lower dimension'},
                {'name': 'Scaling', 'formula': '[[a,0],[0,b]]', 'description': 'Stretches/compresses axes'}
            ],
            'formulas': [
                {'name': 'Linearity', 'formula': 'T(u + v) = T(u) + T(v)'},
                {'name': 'Scalar', 'formula': 'T(cv) = cT(v)'},
                {'name': 'Matrix Representation', 'formula': 'T(v) = Av'},
                {'name': 'Composition', 'formula': '(S ∘ T)(v) = S(T(v))'}
            ],
            'solved_problems': [
                {'problem': 'Find T(2,3) if T(x,y) = (x+y, x-y)', 'steps': ['T(2,3) = (2+3, 2-3)', 'T(2,3) = (5, -1)'], 'answer': '(5, -1)'},
                {'problem': 'Find matrix of T(x,y) = (3x+2y, x-y)', 'steps': ['T(1,0) = (3,1), T(0,1) = (2,-1)', 'Matrix = [[3,2],[1,-1]]'], 'answer': '[[3,2],[1,-1]]'},
                {'problem': 'Is T(x,y) = (x+1, y) linear?', 'steps': ['T(0,0) = (1,0) ≠ (0,0)', 'Linear transformations must map 0 to 0', 'Not linear'], 'answer': 'No, not linear'},
                {'problem': 'Find T∘S if T(x,y)=(2x,y) and S(x,y)=(x+y,y)', 'steps': ['T(S(x,y)) = T(x+y, y)', '= (2(x+y), y)', '= (2x+2y, y)'], 'answer': '(2x+2y, y)'},
                {'problem': 'Find kernel of T(x,y,z) = (x+y, y+z)', 'steps': ['T(x,y,z) = (0,0)', 'x+y=0, y+z=0', 'x=-y, z=-y', 'Kernel: span{(-1,1,-1)}'], 'answer': 'Kernel = span{(-1,1,-1)}'}
            ]
        },
        'Systems of Equations': {
            'definition': 'A system of linear equations is a collection of two or more linear equations involving the same set of variables. Solving means finding values that satisfy all equations simultaneously.',
            'explanation': 'Systems can be solved using substitution, elimination, matrix methods (Gaussian elimination), or Cramer\'s rule. The solution can be unique, infinite, or nonexistent.',
            'examples': [
                {'problem': 'x + y = 5, 2x - y = 1', 'solution': 'Add: 3x = 6, x = 2, y = 3'},
                {'problem': 'x + y + z = 6, 2x + y = 7, x + 2y + z = 8', 'solution': 'x = 2, y = 3, z = 1'},
                {'problem': '2x + 4y = 6, x + 2y = 3', 'solution': 'Same line: infinitely many solutions'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Intersection of Lines</text><line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/><line x1="200" y1="20" x2="200" y2="280" stroke="#333" stroke-width="2"/><line x1="80" y1="220" x2="320" y2="100" stroke="#667eea" stroke-width="2"/><line x1="80" y1="100" x2="320" y2="220" stroke="#764ba2" stroke-width="2"/><circle cx="200" cy="160" r="6" fill="#ff4757"/><text x="210" y="155" font-size="12" fill="#ff4757">Solution (2, 3)</text><text x="200" y="270" font-size="12" fill="#666" text-anchor="middle">Unique solution at intersection</text></svg>',
            'types': [
                {'name': 'Consistent Independent', 'formula': 'Unique solution', 'description': 'Lines intersect at one point'},
                {'name': 'Consistent Dependent', 'formula': 'Infinitely many solutions', 'description': 'Lines coincide'},
                {'name': 'Inconsistent', 'formula': 'No solution', 'description': 'Parallel lines'},
                {'name': 'Homogeneous', 'formula': 'Ax = 0', 'description': 'Always has trivial solution'}
            ],
            'formulas': [
                {'name': 'Matrix Form', 'formula': 'Ax = b'},
                {'name': 'Gaussian Elimination', 'formula': 'Row reduce to echelon form'},
                {'name': "Cramer's Rule", 'formula': 'xᵢ = det(Aᵢ)/det(A)'},
                {'name': 'Inverse Method', 'formula': 'x = A⁻¹b (if A invertible)'}
            ],
            'solved_problems': [
                {'problem': 'Solve: 2x + y = 7, x - y = 2', 'steps': ['Add equations: 3x = 9', 'x = 3', 'y = 7 - 6 = 1'], 'answer': 'x = 3, y = 1'},
                {'problem': 'Solve using matrices: 3x + 2y = 8, x + y = 3', 'steps': ['[[3,2],[1,1]][x,y] = [8,3]', 'det = 3-2 = 1', 'A^-1 = [[1,-2],[-1,3]]', '[x,y] = [[1,-2],[-1,3]][8,3] = [2,1]'], 'answer': 'x = 2, y = 1'},
                {'problem': 'Solve: x + y + z = 6, 2x - y + z = 3, x + 2y - z = 2', 'steps': ['Augmented matrix and row reduce', 'Or solve by substitution/elimination', 'x = 1, y = 2, z = 3'], 'answer': 'x = 1, y = 2, z = 3'},
                {'problem': 'Determine: x + y = 3, 2x + 2y = 7', 'steps': ['Second equation: 2(x+y) = 7', 'But x+y = 3, so 2(3) = 6 ≠ 7', 'Contradiction: no solution'], 'answer': 'No solution (inconsistent)'},
                {'problem': 'Solve: x + 2y - z = 4, 2x + 4y - 2z = 8, 3x + 6y - 3z = 12', 'steps': ['All equations are multiples of first', 'One equation, three unknowns', 'Infinitely many solutions'], 'answer': 'Infinitely many solutions'}
            ]
        }
    },
    'Discrete Mathematics': {
        'Set Theory': {
            'definition': 'Set theory is the branch of mathematics that studies sets, which are collections of objects. It provides the foundation for nearly all of modern mathematics.',
            'explanation': 'Sets are defined by their elements. Key operations include union, intersection, complement, and difference. Venn diagrams help visualize set relationships.',
            'examples': [
                {'problem': 'A = {1,2,3}, B = {2,3,4}', 'solution': 'A∪B = {1,2,3,4}, A∩B = {2,3}'},
                {'problem': 'A = {1,2,3}, U = {1,2,3,4,5}', 'solution': 'A\' = {4,5}'},
                {'problem': 'A = {1,2}, B = {3,4}', 'solution': 'A×B = {(1,3),(1,4),(2,3),(2,4)}'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Venn Diagram</text><circle cx="160" cy="150" r="80" fill="#667eea" opacity="0.2" stroke="#667eea" stroke-width="2"/><circle cx="240" cy="150" r="80" fill="#764ba2" opacity="0.2" stroke="#764ba2" stroke-width="2"/><text x="130" y="155" font-size="14" fill="#667eea" text-anchor="middle">A</text><text x="270" y="155" font-size="14" fill="#764ba2" text-anchor="middle">B</text><text x="200" y="155" font-size="12" fill="#333" text-anchor="middle">A∩B</text><text x="200" y="260" font-size="12" fill="#666" text-anchor="middle">Union, Intersection, Complement</text></svg>',
            'types': [
                {'name': 'Union', 'formula': 'A ∪ B = {x : x ∈ A or x ∈ B}', 'description': 'All elements in either set'},
                {'name': 'Intersection', 'formula': 'A ∩ B = {x : x ∈ A and x ∈ B}', 'description': 'Elements in both sets'},
                {'name': 'Complement', 'formula': 'A\' = {x ∈ U : x ∉ A}', 'description': 'Elements not in A'},
                {'name': 'Difference', 'formula': 'A - B = {x : x ∈ A and x ∉ B}', 'description': 'Elements in A but not B'}
            ],
            'formulas': [
                {'name': 'Union Size', 'formula': '|A ∪ B| = |A| + |B| - |A ∩ B|'},
                {'name': 'De Morgan\'s Law', 'formula': '(A ∪ B)\' = A\' ∩ B\''},
                {'name': 'Power Set', 'formula': '|P(A)| = 2ⁿ'},
                {'name': 'Cartesian Product', 'formula': '|A × B| = |A| × |B|'}
            ],
            'solved_problems': [
                {'problem': 'If |A|=20, |B|=15, |A∩B|=8, find |A∪B|', 'steps': ['|A∪B| = |A| + |B| - |A∩B|', '|A∪B| = 20 + 15 - 8', '|A∪B| = 27'], 'answer': '27'},
                {'problem': 'A={1,2,3,4}, B={3,4,5,6}. Find A-B and B-A.', 'steps': ['A-B = {1,2} (in A, not in B)', 'B-A = {5,6} (in B, not in A)'], 'answer': 'A-B={1,2}, B-A={5,6}'},
                {'problem': 'How many subsets does {a,b,c} have?', 'steps': ['n = 3 elements', 'Number of subsets = 2ⁿ = 2³ = 8', 'List: ∅, {a}, {b}, {c}, {a,b}, {a,c}, {b,c}, {a,b,c}'], 'answer': '8 subsets'},
                {'problem': 'Verify De Morgan: (A∪B)\' = A\'∩B\'', 'steps': ['U={1,2,3,4,5}, A={1,2}, B={2,3}', 'A∪B={1,2,3}, (A∪B)\'={4,5}', 'A\'={3,4,5}, B\'={1,4,5}, A\'∩B\'={4,5}'], 'answer': 'Verified: both equal {4,5}'},
                {'problem': 'In a class: 30 study Math, 25 study Physics, 10 study both. How many study at least one?', 'steps': ['|M∪P| = |M| + |P| - |M∩P|', '|M∪P| = 30 + 25 - 10', '|M∪P| = 45'], 'answer': '45 students'}
            ]
        },
        'Logic & Proofs': {
            'definition': 'Mathematical logic studies formal systems of reasoning. Proofs are rigorous arguments that establish the truth of mathematical statements using logical deduction.',
            'explanation': 'Key logical connectives include AND, OR, NOT, IMPLIES, and IFF. Proof techniques include direct proof, proof by contradiction, proof by contrapositive, and mathematical induction.',
            'examples': [
                {'problem': 'If P then Q. P is true. What about Q?', 'solution': 'By modus ponens: Q must be true'},
                {'problem': 'Prove: If n² is even, then n is even', 'solution': 'Contrapositive: If n is odd, n² is odd. True.'},
                {'problem': 'P ∧ (Q ∨ R)', 'solution': 'True when P is true AND (Q or R is true)'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Truth Table: P → Q</text><rect x="100" y="60" width="200" height="30" fill="#667eea" opacity="0.2"/><text x="150" y="80" font-size="14" fill="#333" text-anchor="middle">P</text><text x="250" y="80" font-size="14" fill="#333" text-anchor="middle">Q</text><text x="150" y="110" font-size="12" fill="#333" text-anchor="middle">T</text><text x="250" y="110" font-size="12" fill="#333" text-anchor="middle">T</text><text x="150" y="140" font-size="12" fill="#333" text-anchor="middle">T</text><text x="250" y="140" font-size="12" fill="#333" text-anchor="middle">F</text><text x="150" y="170" font-size="12" fill="#333" text-anchor="middle">F</text><text x="250" y="170" font-size="12" fill="#333" text-anchor="middle">T</text><text x="150" y="200" font-size="12" fill="#333" text-anchor="middle">F</text><text x="250" y="200" font-size="12" fill="#333" text-anchor="middle">F</text><text x="200" y="240" font-size="12" fill="#666" text-anchor="middle">P→Q: T, F, T, T</text></svg>',
            'types': [
                {'name': 'Direct Proof', 'formula': 'Assume P, show Q', 'description': 'Straightforward deduction'},
                {'name': 'Contrapositive', 'formula': 'Prove ¬Q → ¬P', 'description': 'Equivalent to P → Q'},
                {'name': 'Contradiction', 'formula': 'Assume ¬P, derive contradiction', 'description': 'Proof by impossibility'},
                {'name': 'Induction', 'formula': 'Base case + inductive step', 'description': 'Prove for all natural numbers'}
            ],
            'formulas': [
                {'name': 'Modus Ponens', 'formula': 'P, P→Q ⊢ Q'},
                {'name': 'De Morgan', 'formula': '¬(P∧Q) = ¬P∨¬Q'},
                {'name': 'Contrapositive', 'formula': 'P→Q ≡ ¬Q→¬P'},
                {'name': 'Induction', 'formula': 'P(1) ∧ ∀k(P(k)→P(k+1)) → ∀n P(n)'}
            ],
            'solved_problems': [
                {'problem': 'Prove: sum of two odd numbers is even', 'steps': ['Let a = 2m+1, b = 2n+1', 'a + b = 2m + 1 + 2n + 1 = 2(m+n+1)', '2(m+n+1) is even'], 'answer': 'Proved directly'},
                {'problem': 'Prove √2 is irrational by contradiction', 'steps': ['Assume √2 = p/q (lowest terms)', '2 = p²/q², p² = 2q²', 'p is even, p = 2k', '4k² = 2q², q² = 2k², q is even', 'Contradiction: both divisible by 2'], 'answer': '√2 is irrational'},
                {'problem': 'Prove by induction: 1+2+...+n = n(n+1)/2', 'steps': ['Base: n=1, 1 = 1(2)/2 = 1 ✓', 'Assume true for n=k', 'For n=k+1: sum = k(k+1)/2 + (k+1)', '= (k+1)(k+2)/2 ✓'], 'answer': 'Proved by induction'},
                {'problem': 'Is "If it rains, ground is wet. Ground is wet. Therefore it rained" valid?', 'steps': ['This is affirming the consequent', 'P→Q, Q ⊢ P is NOT valid', 'Ground could be wet for other reasons'], 'answer': 'Invalid (logical fallacy)'},
                {'problem': 'Prove: n² ≥ n for all n ≥ 1', 'steps': ['n² - n = n(n-1)', 'For n ≥ 1: n ≥ 0 and (n-1) ≥ 0', 'Product of non-negative numbers is non-negative', 'n² - n ≥ 0, so n² ≥ n'], 'answer': 'Proved directly'}
            ]
        },
        'Combinatorics': {
            'definition': 'Combinatorics is the branch of mathematics dealing with counting, arrangement, and combination of objects. It includes permutations, combinations, and the pigeonhole principle.',
            'explanation': 'Combinatorial techniques are essential in probability, computer science, and optimization. Key concepts include the multiplication principle, permutations, combinations, and binomial coefficients.',
            'examples': [
                {'problem': 'How many ways to arrange ABC?', 'solution': '3! = 6 ways: ABC, ACB, BAC, BCA, CAB, CBA'},
                {'problem': 'Choose 2 from {A,B,C,D}', 'solution': 'C(4,2) = 6 ways'},
                {'problem': '5-digit codes from digits 0-9', 'solution': '10⁵ = 100,000 possible codes'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Pascal\'s Triangle</text><text x="200" y="60" font-size="14" fill="#333" text-anchor="middle">1</text><text x="200" y="85" font-size="14" fill="#333" text-anchor="middle">1  1</text><text x="200" y="110" font-size="14" fill="#333" text-anchor="middle">1  2  1</text><text x="200" y="135" font-size="14" fill="#333" text-anchor="middle">1  3  3  1</text><text x="200" y="160" font-size="14" fill="#333" text-anchor="middle">1  4  6  4  1</text><text x="200" y="185" font-size="14" fill="#333" text-anchor="middle">1  5  10  10  5  1</text><text x="200" y="220" font-size="12" fill="#666" text-anchor="middle">C(n,k) = n!/(k!(n-k)!)</text></svg>',
            'types': [
                {'name': 'Permutation', 'formula': 'P(n,r) = n!/(n-r)!', 'description': 'Ordered arrangements'},
                {'name': 'Combination', 'formula': 'C(n,r) = n!/(r!(n-r)!)', 'description': 'Unordered selections'},
                {'name': 'With Repetition', 'formula': 'nʳ arrangements', 'description': 'Objects can be reused'},
                {'name': 'Circular', 'formula': '(n-1)! arrangements', 'description': 'Arrangements in a circle'}
            ],
            'formulas': [
                {'name': 'Factorial', 'formula': 'n! = n × (n-1) × ... × 1'},
                {'name': 'Permutation', 'formula': 'P(n,r) = n!/(n-r)!'},
                {'name': 'Combination', 'formula': 'C(n,r) = n!/(r!(n-r)!)'},
                {'name': 'Binomial Theorem', 'formula': '(a+b)ⁿ = Σ C(n,k)aⁿ⁻ᵏbᵏ'}
            ],
            'solved_problems': [
                {'problem': 'How many ways to arrange 5 books on a shelf?', 'steps': ['5! = 5 × 4 × 3 × 2 × 1', '5! = 120'], 'answer': '120 ways'},
                {'problem': 'Choose 3 people from 10 for a committee', 'steps': ['C(10,3) = 10!/(3!×7!)', 'C(10,3) = (10×9×8)/(3×2×1)', 'C(10,3) = 120'], 'answer': '120 ways'},
                {'problem': 'How many 4-letter words from ABCDE (no repetition)?', 'steps': ['P(5,4) = 5!/(5-4)!', 'P(5,4) = 5!/1! = 120'], 'answer': '120 words'},
                {'problem': 'How many ways to choose a president, VP, and secretary from 8 people?', 'steps': ['Order matters (different positions)', 'P(8,3) = 8×7×6', 'P(8,3) = 336'], 'answer': '336 ways'},
                {'problem': 'Expand (x+y)³', 'steps': ['C(3,0)x³ + C(3,1)x²y + C(3,2)xy² + C(3,3)y³', 'x³ + 3x²y + 3xy² + y³'], 'answer': 'x³ + 3x²y + 3xy² + y³'}
            ]
        },
        'Graph Theory': {
            'definition': 'Graph theory studies graphs, which are mathematical structures consisting of vertices (nodes) connected by edges. Graphs model relationships and networks.',
            'explanation': 'Graphs are used to model social networks, transportation systems, computer networks, and many other real-world systems. Key concepts include paths, cycles, connectivity, and coloring.',
            'examples': [
                {'problem': 'Graph with 4 vertices, 5 edges', 'solution': 'Complete graph K₄ has 6 edges; this is K₄ minus one edge'},
                {'problem': 'Is a graph with degrees 2,2,2,2,2 a cycle?', 'solution': 'Yes, C₅ (5-cycle)'},
                {'problem': 'Find shortest path in weighted graph', 'solution': 'Use Dijkstra\'s algorithm'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Graph G = (V, E)</text><circle cx="100" cy="100" r="15" fill="#667eea"/><text x="100" y="105" font-size="12" fill="white" text-anchor="middle">A</text><circle cx="300" cy="100" r="15" fill="#667eea"/><text x="300" y="105" font-size="12" fill="white" text-anchor="middle">B</text><circle cx="100" cy="220" r="15" fill="#667eea"/><text x="100" y="225" font-size="12" fill="white" text-anchor="middle">C</text><circle cx="300" cy="220" r="15" fill="#667eea"/><text x="300" y="225" font-size="12" fill="white" text-anchor="middle">D</text><line x1="115" y1="100" x2="285" y2="100" stroke="#333" stroke-width="2"/><line x1="100" y1="115" x2="100" y2="205" stroke="#333" stroke-width="2"/><line x1="300" y1="115" x2="300" y2="205" stroke="#333" stroke-width="2"/><line x1="115" y1="220" x2="285" y2="220" stroke="#333" stroke-width="2"/><line x1="110" y1="110" x2="290" y2="210" stroke="#333" stroke-width="2"/><text x="200" y="270" font-size="12" fill="#666" text-anchor="middle">V = {A,B,C,D}, E = 5 edges</text></svg>',
            'types': [
                {'name': 'Undirected', 'formula': 'Edges have no direction', 'description': 'Simple connections'},
                {'name': 'Directed', 'formula': 'Edges have direction (arcs)', 'description': 'One-way relationships'},
                {'name': 'Weighted', 'formula': 'Edges have weights/costs', 'description': 'Quantified connections'},
                {'name': 'Complete', 'formula': 'Kₙ: all possible edges', 'description': 'Every pair connected'}
            ],
            'formulas': [
                {'name': 'Handshaking Lemma', 'formula': 'Σ deg(v) = 2|E|'},
                {'name': 'Euler\'s Formula', 'formula': 'V - E + F = 2 (planar graphs)'},
                {'name': 'Complete Graph Edges', 'formula': '|E| = n(n-1)/2'},
                {'name': 'Tree Edges', 'formula': '|E| = |V| - 1'}
            ],
            'solved_problems': [
                {'problem': 'How many edges in K₅ (complete graph with 5 vertices)?', 'steps': ['|E| = n(n-1)/2', '|E| = 5×4/2 = 10'], 'answer': '10 edges'},
                {'problem': 'Can a graph have degrees 1, 2, 3, 4, 5?', 'steps': ['Sum of degrees = 1+2+3+4+5 = 15', 'By handshaking lemma, sum must be even', '15 is odd, impossible'], 'answer': 'No (sum of degrees must be even)'},
                {'problem': 'Find number of faces in planar graph: V=6, E=9', 'steps': ['Euler: V - E + F = 2', '6 - 9 + F = 2', 'F = 5'], 'answer': '5 faces'},
                {'problem': 'Is a graph with 7 vertices and degrees 3,3,3,3,3,3,3 possible?', 'steps': ['Sum = 7×3 = 21', 'Must be even (handshaking lemma)', '21 is odd, impossible'], 'answer': 'No'},
                {'problem': 'How many edges in a tree with 10 vertices?', 'steps': ['Tree: |E| = |V| - 1', '|E| = 10 - 1 = 9'], 'answer': '9 edges'}
            ]
        },
        'Recurrence Relations': {
            'definition': 'A recurrence relation defines a sequence where each term is defined as a function of previous terms. They model recursive processes and divide-and-conquer algorithms.',
            'explanation': 'Recurrence relations are solved using various methods: iteration, characteristic equations, generating functions, and the Master Theorem. They appear in algorithm analysis and discrete dynamical systems.',
            'examples': [
                {'problem': 'Fibonacci: F(n) = F(n-1) + F(n-2)', 'solution': '0, 1, 1, 2, 3, 5, 8, 13, 21, ...'},
                {'problem': 'a(n) = 2a(n-1), a(0) = 1', 'solution': '1, 2, 4, 8, 16, ... (geometric: 2ⁿ)'},
                {'problem': 'T(n) = 2T(n/2) + n', 'solution': 'T(n) = O(n log n) by Master Theorem'}
            ],
            'figure': '<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="300" fill="#f8f9ff"/><text x="200" y="30" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Fibonacci Sequence</text><text x="200" y="60" font-size="14" fill="#333" text-anchor="middle">F(n) = F(n-1) + F(n-2)</text><text x="200" y="90" font-size="12" fill="#666" text-anchor="middle">0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...</text><path d="M 50 250 L 80 245 L 110 245 L 140 235 L 170 220 L 200 195 L 230 160 L 260 115 L 290 60 L 320 40" fill="none" stroke="#667eea" stroke-width="2"/><circle cx="50" cy="250" r="4" fill="#667eea"/><circle cx="80" cy="245" r="4" fill="#667eea"/><circle cx="110" cy="245" r="4" fill="#667eea"/><circle cx="140" cy="235" r="4" fill="#667eea"/><circle cx="170" cy="220" r="4" fill="#667eea"/><circle cx="200" cy="195" r="4" fill="#667eea"/><circle cx="230" cy="160" r="4" fill="#667eea"/><circle cx="260" cy="115" r="4" fill="#667eea"/><circle cx="290" cy="60" r="4" fill="#667eea"/><circle cx="320" cy="40" r="4" fill="#667eea"/><text x="200" y="280" font-size="12" fill="#666" text-anchor="middle">Exponential growth pattern</text></svg>',
            'types': [
                {'name': 'Linear Homogeneous', 'formula': 'a(n) = c₁a(n-1) + c₂a(n-2)', 'description': 'Constant coefficients'},
                {'name': 'Non-homogeneous', 'formula': 'a(n) = f(a(n-1)) + g(n)', 'description': 'Includes external term'},
                {'name': 'Divide & Conquer', 'formula': 'T(n) = aT(n/b) + f(n)', 'description': 'Algorithm analysis'},
                {'name': 'Fibonacci-type', 'formula': 'F(n) = F(n-1) + F(n-2)', 'description': 'Sum of two previous'}
            ],
            'formulas': [
                {'name': 'First-order Linear', 'formula': 'a(n) = r × a(n-1) → a(n) = a(0) × rⁿ'},
                {'name': 'Characteristic Equation', 'formula': 'r² - c₁r - c₂ = 0'},
                {'name': 'Fibonacci Closed Form', 'formula': 'F(n) = (φⁿ - ψⁿ)/√5'},
                {'name': 'Master Theorem', 'formula': 'T(n) = aT(n/b) + O(nᵈ)'}
            ],
            'solved_problems': [
                {'problem': 'Solve: a(n) = 3a(n-1), a(0) = 2', 'steps': ['This is geometric with r = 3', 'a(n) = 2 × 3ⁿ'], 'answer': 'a(n) = 2 × 3ⁿ'},
                {'problem': 'Solve: a(n) = 5a(n-1) - 6a(n-2), a(0)=1, a(1)=4', 'steps': ['Characteristic: r² - 5r + 6 = 0', '(r-2)(r-3) = 0, r = 2, 3', 'a(n) = A×2ⁿ + B×3ⁿ', 'a(0)=1: A+B=1, a(1)=4: 2A+3B=4', 'A=-1, B=2'], 'answer': 'a(n) = -2ⁿ + 2×3ⁿ'},
                {'problem': 'Find F(10) using Fibonacci', 'steps': ['F(0)=0, F(1)=1, F(2)=1, F(3)=2', 'F(4)=3, F(5)=5, F(6)=8', 'F(7)=13, F(8)=21, F(9)=34, F(10)=55'], 'answer': 'F(10) = 55'},
                {'problem': 'Solve T(n) = 2T(n/2) + n, T(1) = 1', 'steps': ['By Master Theorem: a=2, b=2, d=1', 'a = bᵈ, so T(n) = O(n log n)', 'Exact: T(n) = n + n log₂n'], 'answer': 'T(n) = O(n log n)'},
                {'problem': 'Solve: a(n) = 2a(n-1) + 1, a(0) = 0', 'steps': ['a(1) = 1, a(2) = 3, a(3) = 7, a(4) = 15', 'Pattern: a(n) = 2ⁿ - 1', 'Verify: 2(2ⁿ⁻¹-1)+1 = 2ⁿ-2+1 = 2ⁿ-1 ✓'], 'answer': 'a(n) = 2ⁿ - 1'}
            ]
        }
    }
}


@login_required
def topic_detail_view(request, lesson_title, topic_title):
    lesson_content = LESSONS_CONTENT.get(lesson_title, {})
    topic = lesson_content.get(topic_title, {})
    return render(request, 'accounts/topic_detail.html', {
        'lesson_title': lesson_title,
        'topic_title': topic_title,
        'topic': topic
    })


@login_required
def help_view(request):
    faqs = [
        {
            'question': 'How do I use the graphing tools?',
            'answer': 'Navigate to Graphing Tools from the sidebar. Enter your function in the input field and click Plot to visualize. You can adjust the range and zoom level using the controls.'
        },
        {
            'question': 'Can I save my work?',
            'answer': 'Yes! Click the Save button in any tool to save your current work. You can access saved items from your Profile under the My Work section.'
        },
        {
            'question': 'How do I track my progress?',
            'answer': 'Your progress is automatically tracked on the Dashboard. You can view completed lessons, quiz scores, and time spent on each topic.'
        },
        {
            'question': 'Is there a mobile app?',
            'answer': 'We are currently developing a mobile app. In the meantime, the website is fully responsive and works great on mobile browsers.'
        },
        {
            'question': 'How do I reset my password?',
            'answer': 'Go to Settings > Change Password. Enter your current password and new password. If you forgot your password, use the Forgot Password link on the login page.'
        },
        {
            'question': 'Can I collaborate with others?',
            'answer': 'Yes! Join the Community section to connect with other learners, share your work, and collaborate on projects.'
        },
    ]
    return render(request, 'accounts/help.html', {'faqs': faqs})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

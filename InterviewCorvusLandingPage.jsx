import React, { useState, useEffect } from 'react';
import { 
  ChevronDownIcon, 
  ChevronUpIcon, 
  EyeIcon, 
  CodeBracketIcon, 
  ClockIcon, 
  CameraIcon, 
  LanguageIcon, 
  ShieldCheckIcon,
  CheckIcon,
  StarIcon,
  PlayIcon,
  XMarkIcon,
  SunIcon,
  MoonIcon,
  Bars3Icon,
  ArrowUpIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';

const InterviewCorvusLandingPage = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isYearlyPricing, setIsYearlyPricing] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [activeTestimonial, setActiveTestimonial] = useState(0);
  const [expandedFAQ, setExpandedFAQ] = useState(null);
  const [showVideoModal, setShowVideoModal] = useState(false);
  const [email, setEmail] = useState('');
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [showBackToTop, setShowBackToTop] = useState(false);
  const [headerShrunk, setHeaderShrunk] = useState(false);

  // Theme toggle
  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    if (!isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  // Scroll effects
  useEffect(() => {
    const handleScroll = () => {
      setShowBackToTop(window.scrollY > 300);
      setHeaderShrunk(window.scrollY > 100);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Analytics tracking functions
  const trackEvent = (eventName, properties = {}) => {
    // Placeholder for analytics - integrate with Google Analytics, Mixpanel, etc.
    console.log('Analytics Event:', eventName, properties);
    // Example: analytics.track(eventName, properties);
  };

  const handleCTAClick = (location) => {
    trackEvent('CTA_Clicked', { location });
    // Handle CTA action - redirect to download, signup, etc.
  };

  const handleFormSubmit = (formType, data) => {
    trackEvent('Form_Submitted', { formType, ...data });
    // Handle form submission
  };

  // Testimonials data
  const testimonials = [
    {
      name: "Alex Chen",
      role: "Senior Software Engineer at Google",
      avatar: "/api/placeholder/64/64",
      content: "Interview Corvus saved my career! The AI solutions were spot-on and the invisible mode worked flawlessly during my interviews.",
      rating: 5
    },
    {
      name: "Sarah Johnson",
      role: "Full Stack Developer at Meta",
      avatar: "/api/placeholder/64/64",
      content: "The complexity analysis feature helped me understand algorithms better. Got offers from 3 FAANG companies!",
      rating: 5
    },
    {
      name: "Mike Rodriguez",
      role: "Software Developer at Microsoft",
      avatar: "/api/placeholder/64/64",
      content: "Multi-language support is amazing. Switched between Python and Java seamlessly during different interview rounds.",
      rating: 5
    }
  ];

  // FAQ data
  const faqs = [
    {
      question: "Is Interview Corvus detectable during screen sharing?",
      answer: "No! Interview Corvus is specifically designed to remain invisible during screen sharing sessions. With our instant hide feature and global hotkeys, you can make the application disappear completely when needed."
    },
    {
      question: "Which programming languages are supported?",
      answer: "We support 8+ programming languages including Python, Java, JavaScript, C++, C#, Go, Rust, and Ruby. More languages are being added regularly based on user feedback."
    },
    {
      question: "Do I need an OpenAI API key?",
      answer: "Yes, you'll need either an OpenAI API key (GPT-4 or GPT-4o recommended) or an Anthropic API key. This ensures you get the most accurate and up-to-date coding solutions."
    },
    {
      question: "Can I customize the AI prompts?",
      answer: "Absolutely! All prompt templates are fully customizable, including code solution generation, optimization strategies, and complexity analysis parameters."
    },
    {
      question: "Is my data secure?",
      answer: "Yes, we take security seriously. API keys are stored securely using keychain management, and all data is processed locally on your device."
    },
    {
      question: "What platforms are supported?",
      answer: "Interview Corvus supports macOS, Windows, and Linux. We provide native applications for each platform with platform-specific optimizations."
    }
  ];

  // Pricing tiers
  const pricingTiers = [
    {
      name: "Starter",
      price: { monthly: 29, yearly: 290 },
      description: "Perfect for occasional interviews",
      features: [
        "Basic AI coding solutions",
        "5 programming languages",
        "Screenshot analysis",
        "Basic complexity analysis",
        "Email support"
      ],
      popular: false
    },
    {
      name: "Professional",
      price: { monthly: 59, yearly: 590 },
      description: "For serious interview preparation",
      features: [
        "Advanced AI solutions",
        "All 8+ programming languages",
        "Screenshot analysis",
        "Advanced complexity analysis",
        "Code optimization suggestions",
        "Priority support",
        "Custom hotkeys"
      ],
      popular: true
    },
    {
      name: "Enterprise",
      price: { monthly: 99, yearly: 990 },
      description: "For teams and organizations",
      features: [
        "Everything in Professional",
        "Team management",
        "Custom AI models",
        "Advanced analytics",
        "White-label options",
        "24/7 support",
        "Custom integrations"
      ],
      popular: false
    }
  ];

  const ScrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className={`min-h-screen ${isDarkMode ? 'dark' : ''}`}>
      <div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white transition-colors duration-300">
        
        {/* Sticky Navigation */}
        <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
          headerShrunk 
            ? 'bg-white/90 dark:bg-gray-900/90 backdrop-blur-md shadow-lg py-2' 
            : 'bg-transparent py-4'
        }`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">IC</span>
                </div>
                <span className="font-bold text-xl">Interview Corvus</span>
              </div>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center space-x-8">
                <a href="#features" className="hover:text-blue-500 transition-colors">Features</a>
                <a href="#pricing" className="hover:text-blue-500 transition-colors">Pricing</a>
                <a href="#testimonials" className="hover:text-blue-500 transition-colors">Reviews</a>
                <a href="#faq" className="hover:text-blue-500 transition-colors">FAQ</a>
                <a href="#blog" className="hover:text-blue-500 transition-colors">Blog</a>
                
                {/* Language Selector */}
                <select 
                  value={selectedLanguage} 
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="bg-transparent border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm"
                >
                  <option value="en">🇺🇸 EN</option>
                  <option value="es">🇪🇸 ES</option>
                  <option value="fr">🇫🇷 FR</option>
                  <option value="de">🇩🇪 DE</option>
                </select>

                {/* Theme Toggle */}
                <button onClick={toggleTheme} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                  {isDarkMode ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
                </button>

                <button 
                  onClick={() => handleCTAClick('header')}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 font-medium"
                >
                  Download Now
                </button>
              </div>

              {/* Mobile Menu Button */}
              <div className="md:hidden flex items-center space-x-4">
                <button onClick={toggleTheme} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                  {isDarkMode ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
                </button>
                <button onClick={() => setIsMenuOpen(!isMenuOpen)}>
                  <Bars3Icon className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Mobile Menu */}
            {isMenuOpen && (
              <div className="md:hidden mt-4 pb-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex flex-col space-y-4 pt-4">
                  <a href="#features" className="hover:text-blue-500 transition-colors">Features</a>
                  <a href="#pricing" className="hover:text-blue-500 transition-colors">Pricing</a>
                  <a href="#testimonials" className="hover:text-blue-500 transition-colors">Reviews</a>
                  <a href="#faq" className="hover:text-blue-500 transition-colors">FAQ</a>
                  <button 
                    onClick={() => handleCTAClick('mobile-menu')}
                    className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 font-medium text-left"
                  >
                    Download Now
                  </button>
                </div>
              </div>
            )}
          </div>
        </nav>

        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 overflow-hidden">
          {/* Background decoration */}
          <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
          <div className="absolute top-20 left-20 w-72 h-72 bg-blue-500 rounded-full filter blur-3xl opacity-10 animate-pulse"></div>
          <div className="absolute bottom-20 right-20 w-72 h-72 bg-purple-500 rounded-full filter blur-3xl opacity-10 animate-pulse delay-1000"></div>

          <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div className="fade-in-up">
              <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent leading-tight">
                Ace Your Coding Interviews with AI
              </h1>
              <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
                Interview Corvus is your invisible AI assistant that provides real-time coding solutions, 
                complexity analysis, and optimization suggestions while staying completely hidden during screen sharing.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
                <button 
                  onClick={() => handleCTAClick('hero-primary')}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-300 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                >
                  Download Free Trial
                </button>
                <button 
                  onClick={() => setShowVideoModal(true)}
                  className="flex items-center space-x-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-8 py-4 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-300 font-semibold text-lg border-2 border-gray-200 dark:border-gray-600 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                >
                  <PlayIcon className="w-5 h-5" />
                  <span>Watch Demo</span>
                </button>
              </div>

              <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-gray-500 dark:text-gray-400">
                <div className="flex items-center space-x-2">
                  <CheckIcon className="w-4 h-4 text-green-500" />
                  <span>100% Invisible During Screen Share</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckIcon className="w-4 h-4 text-green-500" />
                  <span>8+ Programming Languages</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckIcon className="w-4 h-4 text-green-500" />
                  <span>Real-time AI Solutions</span>
                </div>
              </div>
            </div>
          </div>

          {/* Scroll indicator */}
          <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
            <ChevronDownIcon className="w-6 h-6 text-gray-400" />
          </div>
        </section>

        {/* Product Highlights */}
        <section className="py-20 bg-white dark:bg-gray-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Why Interview Corvus?</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                The only coding interview assistant that stays completely invisible while providing expert-level solutions.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:shadow-lg">
                  <EyeIcon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">100% Invisible</h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Completely hidden during screen sharing. No traces, no detection.
                </p>
              </div>

              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:shadow-lg">
                  <CodeBracketIcon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">AI-Powered Solutions</h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Get complete solutions with detailed explanations using GPT-4.
                </p>
              </div>

              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:shadow-lg">
                  <ClockIcon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Complexity Analysis</h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Understand time and space complexity with detailed explanations.
                </p>
              </div>

              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:shadow-lg">
                  <CameraIcon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Screenshot Analysis</h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Capture problems directly from your screen for instant solutions.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-20 bg-gray-50 dark:bg-gray-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Powerful Features</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                Everything you need to succeed in technical interviews.
              </p>
            </div>

            <div className="grid lg:grid-cols-2 gap-16 items-center">
              {/* Feature 1 */}
              <div className="slide-in-left">
                <div className="bg-white dark:bg-gray-900 rounded-2xl p-8 shadow-xl">
                  <LanguageIcon className="w-12 h-12 text-blue-500 mb-4" />
                  <h3 className="text-2xl font-bold mb-4">Multi-Language Support</h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-6">
                    Support for Python, Java, JavaScript, C++, C#, Go, Rust, and Ruby. 
                    Switch between languages seamlessly during different interview rounds.
                  </p>
                  <ul className="space-y-2">
                    <li className="flex items-center space-x-2">
                      <CheckIcon className="w-4 h-4 text-green-500" />
                      <span>8+ Programming Languages</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckIcon className="w-4 h-4 text-green-500" />
                      <span>Language-specific optimizations</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckIcon className="w-4 h-4 text-green-500" />
                      <span>Best practices for each language</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="slide-in-right">
                <img 
                  src="/api/placeholder/600/400" 
                  alt="Multi-language code examples"
                  className="rounded-2xl shadow-xl"
                />
              </div>

              {/* Feature 2 */}
              <div className="lg:order-2 slide-in-left">
                <div className="bg-white dark:bg-gray-900 rounded-2xl p-8 shadow-xl">
                  <ShieldCheckIcon className="w-12 h-12 text-green-500 mb-4" />
                  <h3 className="text-2xl font-bold mb-4">Global Hotkey Controls</h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-6">
                    Fully customizable hotkeys that work even when the app is not in focus. 
                    Instant hide with panic mode for ultimate stealth.
                  </p>
                  <ul className="space-y-2">
                    <li className="flex items-center space-x-2">
                      <CheckIcon className="w-4 h-4 text-green-500" />
                      <span>Customizable keyboard shortcuts</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckIcon className="w-4 h-4 text-green-500" />
                      <span>Works when app is minimized</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckIcon className="w-4 h-4 text-green-500" />
                      <span>Instant panic mode (Cmd+Q)</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="lg:order-1 slide-in-right">
                <img 
                  src="/api/placeholder/600/400" 
                  alt="Hotkey configuration interface"
                  className="rounded-2xl shadow-xl"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Screenshots/Demo Section */}
        <section className="py-20 bg-white dark:bg-gray-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">See It In Action</h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-12 max-w-2xl mx-auto">
              Watch how Interview Corvus seamlessly integrates into your interview workflow.
            </p>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <div className="group cursor-pointer" onClick={() => setShowVideoModal(true)}>
                <div className="relative rounded-2xl overflow-hidden shadow-xl group-hover:shadow-2xl transition-all duration-300 group-hover:scale-105">
                  <img 
                    src="/api/placeholder/400/300" 
                    alt="Screenshot analysis demo"
                    className="w-full h-64 object-cover"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <PlayIcon className="w-16 h-16 text-white" />
                  </div>
                </div>
                <h3 className="text-lg font-semibold mt-4">Screenshot Analysis</h3>
              </div>

              <div className="group cursor-pointer" onClick={() => setShowVideoModal(true)}>
                <div className="relative rounded-2xl overflow-hidden shadow-xl group-hover:shadow-2xl transition-all duration-300 group-hover:scale-105">
                  <img 
                    src="/api/placeholder/400/300" 
                    alt="AI solution generation"
                    className="w-full h-64 object-cover"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <PlayIcon className="w-16 h-16 text-white" />
                  </div>
                </div>
                <h3 className="text-lg font-semibold mt-4">AI Solution Generation</h3>
              </div>

              <div className="group cursor-pointer" onClick={() => setShowVideoModal(true)}>
                <div className="relative rounded-2xl overflow-hidden shadow-xl group-hover:shadow-2xl transition-all duration-300 group-hover:scale-105">
                  <img 
                    src="/api/placeholder/400/300" 
                    alt="Invisible mode demo"
                    className="w-full h-64 object-cover"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <PlayIcon className="w-16 h-16 text-white" />
                  </div>
                </div>
                <h3 className="text-lg font-semibold mt-4">Invisible Mode</h3>
              </div>
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section id="testimonials" className="py-20 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">What Our Users Say</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Join thousands of developers who landed their dream jobs with Interview Corvus.
              </p>
            </div>

            <div className="relative">
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 md:p-12 text-center max-w-4xl mx-auto">
                <div className="flex justify-center mb-4">
                  {[...Array(testimonials[activeTestimonial].rating)].map((_, i) => (
                    <StarIcon key={i} className="w-6 h-6 text-yellow-400 fill-current" />
                  ))}
                </div>
                <blockquote className="text-xl md:text-2xl text-gray-700 dark:text-gray-300 mb-8 italic leading-relaxed">
                  "{testimonials[activeTestimonial].content}"
                </blockquote>
                <div className="flex items-center justify-center space-x-4">
                  <img 
                    src={testimonials[activeTestimonial].avatar} 
                    alt={testimonials[activeTestimonial].name}
                    className="w-16 h-16 rounded-full"
                  />
                  <div className="text-left">
                    <div className="font-semibold text-lg">{testimonials[activeTestimonial].name}</div>
                    <div className="text-gray-600 dark:text-gray-400">{testimonials[activeTestimonial].role}</div>
                  </div>
                </div>
              </div>

              {/* Navigation dots */}
              <div className="flex justify-center mt-8 space-x-2">
                {testimonials.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setActiveTestimonial(index)}
                    className={`w-3 h-3 rounded-full transition-all duration-300 ${
                      index === activeTestimonial 
                        ? 'bg-blue-500 w-8' 
                        : 'bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="py-20 bg-white dark:bg-gray-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
                Choose the plan that fits your interview preparation needs.
              </p>

              {/* Pricing Toggle */}
              <div className="flex items-center justify-center space-x-4 mb-8">
                <span className={`text-lg ${!isYearlyPricing ? 'text-blue-500 font-semibold' : 'text-gray-500'}`}>
                  Monthly
                </span>
                <button
                  onClick={() => setIsYearlyPricing(!isYearlyPricing)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 ${
                    isYearlyPricing ? 'bg-blue-500' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-300 ${
                      isYearlyPricing ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
                <span className={`text-lg ${isYearlyPricing ? 'text-blue-500 font-semibold' : 'text-gray-500'}`}>
                  Yearly
                  <span className="ml-1 text-sm bg-green-100 text-green-800 px-2 py-1 rounded-full">Save 17%</span>
                </span>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {pricingTiers.map((tier, index) => (
                <div 
                  key={tier.name}
                  className={`relative rounded-2xl p-8 transition-all duration-300 hover:scale-105 ${
                    tier.popular 
                      ? 'bg-gradient-to-b from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-2 border-blue-500 shadow-2xl' 
                      : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-xl'
                  }`}
                >
                  {tier.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <span className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-2 rounded-full text-sm font-semibold">
                        Most Popular
                      </span>
                    </div>
                  )}

                  <div className="text-center mb-8">
                    <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
                    <p className="text-gray-600 dark:text-gray-300 mb-4">{tier.description}</p>
                    <div className="mb-4">
                      <span className="text-4xl font-bold">
                        ${isYearlyPricing ? tier.price.yearly : tier.price.monthly}
                      </span>
                      <span className="text-gray-600 dark:text-gray-300 ml-2">
                        /{isYearlyPricing ? 'year' : 'month'}
                      </span>
                    </div>
                    {isYearlyPricing && (
                      <p className="text-sm text-green-600 dark:text-green-400">
                        Save ${(tier.price.monthly * 12) - tier.price.yearly} yearly
                      </p>
                    )}
                  </div>

                  <ul className="space-y-4 mb-8">
                    {tier.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center space-x-3">
                        <CheckIcon className="w-5 h-5 text-green-500 flex-shrink-0" />
                        <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <button 
                    onClick={() => {
                      handleCTAClick('pricing');
                      trackEvent('Pricing_Plan_Selected', { plan: tier.name, billing: isYearlyPricing ? 'yearly' : 'monthly' });
                    }}
                    className={`w-full py-3 px-6 rounded-xl font-semibold transition-all duration-300 ${
                      tier.popular
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 shadow-lg hover:shadow-xl'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                  >
                    Get Started
                  </button>
                </div>
              ))}
            </div>

            <div className="text-center mt-12">
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                All plans include a 14-day free trial. No credit card required.
              </p>
              <div className="flex flex-wrap justify-center gap-8 text-sm text-gray-500">
                <span>✓ 14-day free trial</span>
                <span>✓ No setup fees</span>
                <span>✓ Cancel anytime</span>
                <span>✓ 30-day money back guarantee</span>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section id="faq" className="py-20 bg-gray-50 dark:bg-gray-800">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Frequently Asked Questions</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Got questions? We've got answers.
              </p>
            </div>

            <div className="space-y-4">
              {faqs.map((faq, index) => (
                <div 
                  key={index}
                  className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg overflow-hidden"
                >
                  <button
                    onClick={() => setExpandedFAQ(expandedFAQ === index ? null : index)}
                    className="w-full px-8 py-6 text-left flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-300"
                  >
                    <span className="text-lg font-semibold pr-4">{faq.question}</span>
                    {expandedFAQ === index ? (
                      <ChevronUpIcon className="w-5 h-5 text-blue-500 flex-shrink-0" />
                    ) : (
                      <ChevronDownIcon className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    )}
                  </button>
                  {expandedFAQ === index && (
                    <div className="px-8 pb-6">
                      <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                        {faq.answer}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Customer Logos */}
        <section className="py-12 bg-white dark:bg-gray-900 border-y border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <p className="text-center text-gray-500 dark:text-gray-400 mb-8">
              Trusted by developers at top companies
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8 items-center opacity-60">
              <img src="/api/placeholder/120/60" alt="Google" className="h-8 mx-auto grayscale hover:grayscale-0 transition-all duration-300" />
              <img src="/api/placeholder/120/60" alt="Microsoft" className="h-8 mx-auto grayscale hover:grayscale-0 transition-all duration-300" />
              <img src="/api/placeholder/120/60" alt="Amazon" className="h-8 mx-auto grayscale hover:grayscale-0 transition-all duration-300" />
              <img src="/api/placeholder/120/60" alt="Meta" className="h-8 mx-auto grayscale hover:grayscale-0 transition-all duration-300" />
              <img src="/api/placeholder/120/60" alt="Netflix" className="h-8 mx-auto grayscale hover:grayscale-0 transition-all duration-300" />
              <img src="/api/placeholder/120/60" alt="Apple" className="h-8 mx-auto grayscale hover:grayscale-0 transition-all duration-300" />
            </div>
          </div>
        </section>

        {/* Blog/Resources Section */}
        <section id="blog" className="py-20 bg-gray-50 dark:bg-gray-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Latest from Our Blog</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Tips, strategies, and insights to help you ace your interviews.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <article className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 group">
                <img 
                  src="/api/placeholder/400/250" 
                  alt="Interview tips"
                  className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="p-6">
                  <div className="flex items-center space-x-2 mb-3">
                    <DocumentTextIcon className="w-4 h-4 text-blue-500" />
                    <span className="text-sm text-blue-500 font-medium">Interview Tips</span>
                  </div>
                  <h3 className="text-xl font-bold mb-2 group-hover:text-blue-500 transition-colors">
                    10 Essential Coding Interview Patterns You Must Know
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Master these fundamental patterns to solve 80% of coding interview problems with confidence.
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">5 min read</span>
                    <a href="#" className="text-blue-500 hover:text-blue-600 transition-colors">Read more →</a>
                  </div>
                </div>
              </article>

              <article className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 group">
                <img 
                  src="/api/placeholder/400/250" 
                  alt="Success story"
                  className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="p-6">
                  <div className="flex items-center space-x-2 mb-3">
                    <AcademicCapIcon className="w-4 h-4 text-green-500" />
                    <span className="text-sm text-green-500 font-medium">Success Story</span>
                  </div>
                  <h3 className="text-xl font-bold mb-2 group-hover:text-blue-500 transition-colors">
                    How Sarah Landed a $200K Job at Google Using Interview Corvus
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    A complete breakdown of the preparation strategy that led to multiple FAANG offers.
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">8 min read</span>
                    <a href="#" className="text-blue-500 hover:text-blue-600 transition-colors">Read more →</a>
                  </div>
                </div>
              </article>

              <article className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 group">
                <img 
                  src="/api/placeholder/400/250" 
                  alt="Technical guide"
                  className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="p-6">
                  <div className="flex items-center space-x-2 mb-3">
                    <CodeBracketIcon className="w-4 h-4 text-purple-500" />
                    <span className="text-sm text-purple-500 font-medium">Technical Guide</span>
                  </div>
                  <h3 className="text-xl font-bold mb-2 group-hover:text-blue-500 transition-colors">
                    Understanding Time Complexity: A Visual Guide
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Master Big O notation with interactive examples and real-world applications.
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">12 min read</span>
                    <a href="#" className="text-blue-500 hover:text-blue-600 transition-colors">Read more →</a>
                  </div>
                </div>
              </article>
            </div>

            <div className="text-center mt-12">
              <a 
                href="#" 
                className="inline-flex items-center space-x-2 bg-blue-500 text-white px-6 py-3 rounded-xl hover:bg-blue-600 transition-colors duration-300 font-medium"
              >
                <span>View All Articles</span>
                <DocumentTextIcon className="w-5 h-5" />
              </a>
            </div>
          </div>
        </section>

        {/* Newsletter Section */}
        <section className="py-20 bg-gradient-to-r from-blue-500 to-purple-600">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Stay Ahead of the Competition
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Get weekly interview tips, coding patterns, and exclusive strategies delivered straight to your inbox.
            </p>

            <form 
              onSubmit={(e) => {
                e.preventDefault();
                handleFormSubmit('newsletter', { email });
                setEmail('');
              }}
              className="max-w-md mx-auto"
            >
              <div className="flex gap-4">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email address"
                  required
                  className="flex-1 px-6 py-4 rounded-xl border-0 focus:ring-4 focus:ring-blue-300 focus:outline-none text-gray-900"
                />
                <button 
                  type="submit"
                  className="bg-white text-blue-600 px-8 py-4 rounded-xl hover:bg-gray-100 transition-colors duration-300 font-semibold whitespace-nowrap"
                >
                  Subscribe
                </button>
              </div>
            </form>

            <p className="text-sm text-blue-100 mt-4">
              Join 10,000+ developers. Unsubscribe anytime.
            </p>
          </div>
        </section>

        {/* Contact Form Section */}
        <section className="py-20 bg-white dark:bg-gray-900">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Get in Touch</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Have questions? We'd love to hear from you.
              </p>
            </div>

            <div className="grid lg:grid-cols-2 gap-12">
              <div>
                <h3 className="text-2xl font-bold mb-6">Contact Information</h3>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center mt-1">
                      <span className="text-white text-xs">✉</span>
                    </div>
                    <div>
                      <p className="font-semibold">Email</p>
                      <p className="text-gray-600 dark:text-gray-300">support@interviewcorvus.com</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center mt-1">
                      <span className="text-white text-xs">💬</span>
                    </div>
                    <div>
                      <p className="font-semibold">Telegram</p>
                      <p className="text-gray-600 dark:text-gray-300">@pavlin_share</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center mt-1">
                      <span className="text-white text-xs">📞</span>
                    </div>
                    <div>
                      <p className="font-semibold">Support Hours</p>
                      <p className="text-gray-600 dark:text-gray-300">Mon-Fri, 9AM-6PM UTC</p>
                    </div>
                  </div>
                </div>
              </div>

              <form 
                onSubmit={(e) => {
                  e.preventDefault();
                  handleFormSubmit('contact', contactForm);
                  setContactForm({ name: '', email: '', message: '' });
                }}
                className="space-y-6"
              >
                <div>
                  <label htmlFor="name" className="block text-sm font-medium mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    value={contactForm.name}
                    onChange={(e) => setContactForm({...contactForm, name: e.target.value})}
                    required
                    className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-4 focus:ring-blue-300 focus:border-transparent transition-all duration-300"
                  />
                </div>

                <div>
                  <label htmlFor="contact-email" className="block text-sm font-medium mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="contact-email"
                    value={contactForm.email}
                    onChange={(e) => setContactForm({...contactForm, email: e.target.value})}
                    required
                    className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-4 focus:ring-blue-300 focus:border-transparent transition-all duration-300"
                  />
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-medium mb-2">
                    Message
                  </label>
                  <textarea
                    id="message"
                    value={contactForm.message}
                    onChange={(e) => setContactForm({...contactForm, message: e.target.value})}
                    required
                    rows={6}
                    className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-4 focus:ring-blue-300 focus:border-transparent transition-all duration-300 resize-none"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-300 font-semibold transform hover:scale-105"
                >
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {/* Company Info */}
              <div>
                <div className="flex items-center space-x-2 mb-6">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-sm">IC</span>
                  </div>
                  <span className="font-bold text-xl">Interview Corvus</span>
                </div>
                <p className="text-gray-400 mb-6 leading-relaxed">
                  The AI-powered invisible assistant that helps developers ace their coding interviews with confidence.
                </p>
                <div className="flex space-x-4">
                  <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors duration-300">
                    <span className="text-sm">📧</span>
                  </a>
                  <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors duration-300">
                    <span className="text-sm">💬</span>
                  </a>
                  <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors duration-300">
                    <span className="text-sm">🐙</span>
                  </a>
                </div>
              </div>

              {/* Product */}
              <div>
                <h3 className="font-semibold text-lg mb-6">Product</h3>
                <ul className="space-y-4">
                  <li><a href="#features" className="text-gray-400 hover:text-white transition-colors">Features</a></li>
                  <li><a href="#pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</a></li>
                  <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Download</a></li>
                  <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Releases</a></li>
                  <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Roadmap</a></li>
                </ul>
              </div>

              {/* Resources */}
              <div>
                <h3 className="font-semibold text-lg mb-6">Resources</h3>
                <ul className="space-y-4">
                  <li><a href="#blog" className="text-gray-400 hover:text-white transition-colors">Blog</a></li>
                  <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Documentation</a></li>
                  <li><a href="#" className="text-gray-400 hover:text-white transition-colors">API Reference</a></li>
                  <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Tutorials</a></li>
                  <li><a href="#faq" className="text-gray-400 hover:text-white transition-colors">FAQ</a></li>
                </ul>
              </div>

              {/* Support */}
              <div>
                <h3 className="font-semibold text-lg mb-6">Support</h3>
                <ul className="space-y-4">
                  <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Contact Us</a></li>
                  <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Help Center</a></li>
                  <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</a></li>
                  <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Terms of Service</a></li>
                  <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Status</a></li>
                </ul>
              </div>
            </div>

            <hr className="border-gray-800 my-12" />

            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 mb-4 md:mb-0">
                © 2024 Interview Corvus. All rights reserved. Created by{' '}
                <a href="https://t.me/pavlin_share" className="text-blue-400 hover:text-blue-300 transition-colors">
                  Nikolay Pavlin
                </a>
              </p>
              <div className="flex items-center space-x-6 text-gray-400">
                <span>Made with ❤️ for developers</span>
                <span>•</span>
                <a href="#" className="hover:text-white transition-colors">Support</a>
              </div>
            </div>
          </div>
        </footer>

        {/* Video Modal */}
        {showVideoModal && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 max-w-4xl w-full relative">
              <button
                onClick={() => setShowVideoModal(false)}
                className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
              <h3 className="text-2xl font-bold mb-4">Interview Corvus Demo</h3>
              <div className="aspect-video bg-gray-100 dark:bg-gray-800 rounded-xl flex items-center justify-center">
                <p className="text-gray-500">Video Player Placeholder</p>
                {/* Replace with actual video player */}
              </div>
            </div>
          </div>
        )}

        {/* Chat Widget Placeholder */}
        <div className="fixed bottom-6 right-6 z-40">
          <button 
            onClick={() => trackEvent('Chat_Widget_Clicked')}
            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transform hover:scale-110 transition-all duration-300"
          >
            <ChatBubbleLeftRightIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Sticky Mobile CTA */}
        <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 p-4 z-30 md:hidden">
          <button 
            onClick={() => handleCTAClick('sticky-mobile')}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-xl font-semibold"
          >
            Download Free Trial
          </button>
        </div>

        {/* Back to Top Button */}
        {showBackToTop && (
          <button
            onClick={ScrollToTop}
            className="fixed bottom-24 right-6 bg-gray-800 dark:bg-gray-700 text-white p-3 rounded-full shadow-lg hover:shadow-xl transform hover:scale-110 transition-all duration-300 z-40"
          >
            <ArrowUpIcon className="w-5 h-5" />
          </button>
        )}

        {/* Custom CSS for animations */}
        <style jsx>{`
          .fade-in-up {
            animation: fadeInUp 1s ease-out;
          }
          
          .slide-in-left {
            animation: slideInLeft 0.8s ease-out;
          }
          
          .slide-in-right {
            animation: slideInRight 0.8s ease-out;
          }
          
          @keyframes fadeInUp {
            from {
              opacity: 0;
              transform: translateY(30px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          
          @keyframes slideInLeft {
            from {
              opacity: 0;
              transform: translateX(-30px);
            }
            to {
              opacity: 1;
              transform: translateX(0);
            }
          }
          
          @keyframes slideInRight {
            from {
              opacity: 0;
              transform: translateX(30px);
            }
            to {
              opacity: 1;
              transform: translateX(0);
            }
          }
          
          .bg-grid-pattern {
            background-image: 
              linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px);
            background-size: 20px 20px;
          }
        `}</style>
      </div>
    </div>
  );
};

export default InterviewCorvusLandingPage;

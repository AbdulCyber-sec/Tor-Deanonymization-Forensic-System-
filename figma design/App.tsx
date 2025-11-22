import { useState } from "react";
import { Shield, Target, Layers, Activity, BarChart3, Users, BookOpen } from "lucide-react";
import { Button } from "./components/ui/button";
import { HeroSection } from "./components/HeroSection";
import { ProblemSolutionSection } from "./components/ProblemSolutionSection";
import { MethodologySection } from "./components/MethodologySection";
import { PredictionDashboard } from "./components/PredictionDashboard";
import { CapabilitiesSection } from "./components/CapabilitiesSection";
import { ValidationSection } from "./components/ValidationSection";
import { TeamSection } from "./components/TeamSection";

type Section = 
  | "hero"
  | "problem"
  | "methodology"
  | "dashboard"
  | "capabilities"
  | "validation"
  | "team";

export default function App() {
  const [activeSection, setActiveSection] = useState<Section>("hero");

  const navigationItems = [
    { id: "hero" as Section, label: "Home", icon: Shield },
    { id: "problem" as Section, label: "Problem & Solution", icon: Target },
    { id: "methodology" as Section, label: "Methodology", icon: Layers },
    { id: "dashboard" as Section, label: "Live Dashboard", icon: Activity },
    { id: "capabilities" as Section, label: "Capabilities", icon: BookOpen },
    { id: "validation" as Section, label: "Validation", icon: BarChart3 },
    { id: "team" as Section, label: "Team", icon: Users },
  ];

  const scrollToSection = (sectionId: Section) => {
    setActiveSection(sectionId);
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <div className="dark min-h-screen bg-background text-foreground">
      {/* Skip to content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded"
      >
        Skip to main content
      </a>

      {/* Fixed Navigation Header */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-card/95 backdrop-blur-md border-b border-border" aria-label="Main navigation">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <Shield className="w-6 h-6 text-primary" />
              <span className="text-lg font-semibold">TGNP System</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-1">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Button
                    key={item.id}
                    variant={activeSection === item.id ? "default" : "ghost"}
                    size="sm"
                    onClick={() => scrollToSection(item.id)}
                    className="gap-2"
                    aria-label={`Navigate to ${item.label}`}
                    aria-current={activeSection === item.id ? "page" : undefined}
                  >
                    <Icon className="w-4 h-4" aria-hidden="true" />
                    {item.label}
                  </Button>
                );
              })}
            </div>

            {/* Mobile Menu Toggle */}
            <Button
              variant="outline"
              size="sm"
              className="md:hidden"
              onClick={() => {
                const mobileMenu = document.getElementById("mobile-menu");
                if (mobileMenu) {
                  mobileMenu.classList.toggle("hidden");
                }
              }}
              aria-label="Toggle mobile menu"
              aria-expanded="false"
            >
              Menu
            </Button>
          </div>

          {/* Mobile Navigation */}
          <div id="mobile-menu" className="hidden md:hidden pb-4" role="menu">
            <div className="flex flex-col gap-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Button
                    key={item.id}
                    variant={activeSection === item.id ? "default" : "ghost"}
                    onClick={() => {
                      scrollToSection(item.id);
                      document.getElementById("mobile-menu")?.classList.add("hidden");
                    }}
                    className="justify-start gap-2"
                    aria-label={`Navigate to ${item.label}`}
                    role="menuitem"
                  >
                    <Icon className="w-4 h-4" aria-hidden="true" />
                    {item.label}
                  </Button>
                );
              })}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-16" id="main-content" role="main">
        <section id="hero" aria-label="Hero section">
          <HeroSection onNavigate={scrollToSection} />
        </section>

        <section id="problem" aria-label="Problem and solution">
          <ProblemSolutionSection />
        </section>

        <section id="methodology" aria-label="Methodology">
          <MethodologySection />
        </section>

        <section id="dashboard" aria-label="Live prediction dashboard">
          <PredictionDashboard />
        </section>

        <section id="capabilities" aria-label="System capabilities">
          <CapabilitiesSection />
        </section>

        <section id="validation" aria-label="Validation results">
          <ValidationSection />
        </section>

        <section id="team" aria-label="Team and about">
          <TeamSection />
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-8 mt-16" role="contentinfo">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Shield className="w-5 h-5 text-primary" />
                <span className="font-semibold">TGNP System</span>
              </div>
              <p className="text-sm text-muted-foreground">
                TOR Guard Node Prediction System for law enforcement and cybercrime investigators.
              </p>
            </div>

            <div>
              <h3 className="mb-4">Quick Links</h3>
              <div className="flex flex-col gap-2">
                <button
                  onClick={() => scrollToSection("dashboard")}
                  className="text-sm text-muted-foreground hover:text-primary text-left"
                >
                  Live Dashboard
                </button>
                <button
                  onClick={() => scrollToSection("methodology")}
                  className="text-sm text-muted-foreground hover:text-primary text-left"
                >
                  Methodology
                </button>
                <button
                  onClick={() => scrollToSection("validation")}
                  className="text-sm text-muted-foreground hover:text-primary text-left"
                >
                  Validation Results
                </button>
              </div>
            </div>

            <div>
              <h3 className="mb-4">Legal & Ethics</h3>
              <p className="text-sm text-muted-foreground">
                This system operates exclusively on publicly available data and does not break encryption or violate privacy laws.
              </p>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-border text-center text-sm text-muted-foreground">
            <p>© 2025 TGNP System. For law enforcement and authorized investigative use only.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
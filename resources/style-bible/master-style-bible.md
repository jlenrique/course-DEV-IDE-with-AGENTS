# Master Style Bible: JCPH Medical Education

**Version**: 1.0  
**Effective Date**: 2026-03-25  
**Course Scope**: Intrapreneurship for Physicians Certificate Program  
**Review Cycle**: Per course development cycle

## Brand Foundation

### Mission Statement
Create professional medical education experiences that respect physician expertise while delivering transformative learning through high-quality, accessible content that fits into demanding clinical schedules.

### Brand Personality
- **Authoritative**: Evidence-based, credible, respecting medical expertise
- **Practical**: Immediately applicable, real-world focused, time-efficient
- **Innovative**: Forward-thinking, technology-enabled, breakthrough approaches
- **Accessible**: Inclusive, clear communication, barrier-free learning

## Visual Identity System

### Color Palette

#### Primary Colors
```yaml
JCPH_Navy: 
  hex: "#1e3a5f"
  rgb: "30, 58, 95"
  usage: "Primary headers, navigation, authority elements"
  
Medical_Teal:
  hex: "#4a90a4" 
  rgb: "74, 144, 164"
  usage: "Secondary accents, interactive elements, progress indicators"
```

#### Supporting Colors
```yaml
Clean_White:
  hex: "#ffffff"
  usage: "Background, text on dark elements, clean separation"
  
Soft_Gray:
  hex: "#f8f9fa"
  usage: "Section backgrounds, subtle separation, cards"
  
Success_Green:
  hex: "#28a745"
  usage: "Completion, success states, positive feedback"
  
Alert_Orange:
  hex: "#fd7e14"
  usage: "Warnings, attention items, important callouts"
  
Error_Red:
  hex: "#dc3545" 
  usage: "Errors, critical information, urgent attention"
```

#### Accessibility Requirements
- **Minimum Contrast**: WCAG 2.1 AA (4.5:1 for normal text, 3:1 for large text)
- **Color Independence**: Information never conveyed by color alone
- **High Contrast Mode**: All content readable in high contrast browser settings

### Typography System

#### Heading Hierarchy
```yaml
Primary_Font: "Montserrat"
  weights: [400, 600, 700]
  usage: "Headlines, module titles, major section headers"
  characteristics: "Clean, professional, executive presence"

Secondary_Font: "Open Sans" 
  weights: [400, 600]
  usage: "Body text, descriptions, general content"
  characteristics: "Readable, accessible, physician-friendly"
  
Technical_Font: "Source Sans Pro"
  weights: [400, 600]
  usage: "Data, statistics, technical specifications"
  characteristics: "Clear numbers, medical terminology, charts"
```

#### Responsive Typography Scale
```yaml
H1: "32px / 38px line-height (desktop), 28px / 34px (mobile)"
H2: "28px / 34px line-height (desktop), 24px / 30px (mobile)" 
H3: "24px / 30px line-height (desktop), 20px / 26px (mobile)"
H4: "20px / 26px line-height (desktop), 18px / 24px (mobile)"
Body: "16px / 24px line-height (desktop), 16px / 24px (mobile)"
Caption: "14px / 20px line-height (all devices)"
```

### Imagery Standards

#### Photography Guidelines
```yaml
Style_Direction: "Authentic clinical environments with natural lighting"
Subjects: "Real healthcare professionals in genuine work settings"
Composition: "Clean, uncluttered, professional focus"
Quality: "High-resolution, crisp detail, professional photography standards"
Diversity: "Representative of modern healthcare workforce"
```

#### Illustration Standards
```yaml
Vector_Style: "Clean, minimal, professional medical aesthetic"
Color_Usage: "Consistent with brand palette, avoid cartoon aesthetics"
Technical_Diagrams: "Clear, labeled, educational focus"
Icons: "Simple, recognizable, consistent line weights"
Medical_Content: "Accurate, respectful, appropriate complexity"
```

#### Chart and Data Visualization
```yaml
Background: "Dark navy for high contrast on mobile devices"
Data_Colors: "Teal primary, white secondary, orange accents for emphasis"
Typography: "Source Sans Pro for numbers and labels"
Style: "Clean, minimal, emphasis on signal over noise"
Mobile_Optimization: "Large touch targets, readable at small sizes"
```

## Voice and Content Guidelines

### Target Audience Profile
```yaml
Primary_Audience: "Practicing physicians"
Context: "Time-constrained, evidence-driven, professional expertise"
Learning_Preferences: "Practical application, immediate relevance, efficient delivery"
Technology_Comfort: "Moderate to high, mobile-first consumption patterns"
Respect_Requirements: "Professional peer-level communication, avoid condescension"
```

### Voice Characteristics

#### Tone Attributes
- **Clear and Direct**: No unnecessary complexity or academic jargon without definition
- **Respectful**: Acknowledges professional expertise and time constraints  
- **Inclusive**: Accessible language that doesn't exclude any healthcare professional
- **Practical**: Focus on real-world application and immediate utility
- **Evidence-Based**: Credible sources, peer-reviewed foundation where appropriate

#### Writing Style Guidelines
```yaml
Sentence_Length: "Vary between 12-20 words average, shorter for key concepts"
Paragraph_Length: "3-5 sentences maximum, scannable for mobile reading"
Jargon_Policy: "Define medical terminology on first use, avoid business buzzwords"
Active_Voice: "Preferred for clarity and directness"
Personal_Address: "Use 'you' to create direct engagement"
```

### Content Structure Templates

#### Learning Module Pattern
```markdown
1. Opening Hook (30 seconds): Why this matters now
2. Learning Objectives (clear, specific, actionable)
3. Core Content (chunked in 3-5 minute segments)
4. Real-World Application (concrete examples)
5. Knowledge Check (immediate feedback)
6. Next Steps (clear progression)
```

#### Assessment Guidelines
```yaml
Question_Style: "Scenario-based when possible, avoid pure recall"
Feedback: "Specific, educational, builds understanding"
Difficulty_Progression: "Start accessible, build to application level"
Time_Respect: "Efficient completion, no unnecessary complexity"
```

## Tool-Specific Translation Guidelines

### Gamma Slide Generation
```yaml
Prompt_Template: |
  "Create professional medical education slides with:
  - Color scheme: Navy blue primary (#1e3a5f), teal accents (#4a90a4)
  - Typography: Clean, executive presentation style
  - Layout: Minimal, high contrast, mobile-optimized
  - Aesthetic: Corporate medical education, not consumer health
  - Content focus: [SPECIFIC_TOPIC]"
```

### Midjourney Image Generation  
```yaml
Prompt_Template: |
  "Professional hospital/clinical setting, natural lighting, authentic medical 
  environment, modern healthcare facility, clean corporate aesthetic, 
  4K quality --ar 16:9 --style corporate --v 6"
  
Style_Modifiers:
  - "photorealistic, professional medical photography"
  - "authentic clinical environment, not staged"  
  - "diverse healthcare workforce representation"
```

### Canva Design Standards
```yaml
Brand_Kit_Upload:
  - JCPH logo variants
  - Color palette (hex codes)
  - Font selections (Montserrat, Open Sans)
  - Template library for consistent layouts
```

### Video Production (Descript/CapCut)
```yaml
Visual_Standards:
  Background: "Clean, professional clinical or office environment"
  Lighting: "Natural or professional lighting setup"
  Framing: "Professional presentation framing"
  
Audio_Standards:
  Quality: "Studio sound enhancement via Descript"
  Pace: "Natural physician speaking pace, edited for efficiency"
  Captions: "Professional accuracy, synchronized timing"
```

### ElevenLabs Voice Generation
```yaml
Voice_Profile: "Professional, authoritative, clear articulation"
Pace: "Moderate, appropriate for medical content"
Tone: "Respectful peer-to-peer communication"
Quality: "Professional narration standard"
```

## Quality Assurance Standards

### Brand Compliance Checklist
- [ ] **Color Accuracy**: All colors match specified hex values
- [ ] **Typography Consistency**: Correct fonts and hierarchy used
- [ ] **Accessibility Standards**: WCAG 2.1 AA compliance verified
- [ ] **Voice Alignment**: Content matches tone and style guidelines
- [ ] **Mobile Optimization**: Readable and functional on mobile devices
- [ ] **Professional Standards**: Appropriate for physician audience

### Tool Output Verification
- [ ] **Gamma Slides**: Brand colors, professional layout, mobile-readable
- [ ] **Midjourney Images**: Authentic clinical feel, diverse representation
- [ ] **Canva Graphics**: Consistent with brand kit, accessible contrast
- [ ] **Video Content**: Professional quality, proper captions
- [ ] **Audio Content**: Clear, professional, synchronized with visuals

## Version Control and Evolution

### Update Triggers
- **Course Development Feedback**: Learner and instructor input on brand effectiveness
- **Tool Capability Changes**: New features in design/generation tools
- **Accessibility Requirements**: WCAG updates or institutional requirements
- **Brand Evolution**: JCPH institutional branding changes

### Change Management Process
1. **Proposal Phase**: Documented rationale for style bible updates
2. **Review Phase**: Stakeholder review including accessibility compliance
3. **Testing Phase**: Sample content generation with updated guidelines  
4. **Implementation Phase**: Tool prompt updates and agent retraining
5. **Monitoring Phase**: Quality assurance verification across production outputs

This style bible ensures consistent, professional, accessible medical education content across all production tools and platforms.
# Canvas + CourseArc Platform Allocation Policy

**Version**: 1.0  
**Effective Date**: 2026-03-25  
**Review Cycle**: Quarterly  
**Scope**: All multi-agent course production workflows

## Policy Overview

This document establishes consistent criteria for allocating instructional activities between Canvas (primary LMS) and CourseArc (embedded lesson environment) to optimize learning experience while maintaining operational efficiency.

## Core Allocation Principles

### Canvas as Academic Spine
Canvas serves as the **primary learning management system** and maintains:
- **System of Record**: Official course structure, grades, and institutional data
- **Academic Infrastructure**: Discussions, assessments, due dates, and communication
- **Instructor Workflow**: SpeedGrader, analytics dashboard, and gradebook management
- **Integration Hub**: Launch point for all other platforms and tools

### CourseArc as Experience Layer  
CourseArc serves as the **premium content delivery environment** for:
- **High-Presence Learning**: Polished, guided lesson experiences with narrative control
- **Media-Rich Content**: Embedded videos, audio, and interactive multimedia
- **Modern User Experience**: Web-page aesthetics that enhance learner engagement
- **Built-in Interactivity**: Native interactive blocks (sorting, flip cards, polls)

## Decision Framework

### Canvas Platform Selection Criteria

**REQUIRED for Canvas:**
- **Graded Assessments**: Any activity requiring gradebook integration
- **Peer Discussions**: Social learning requiring visible peer exchange  
- **Instructor Facilitation**: Activities needing SpeedGrader or instructor intervention
- **Institutional Reporting**: Content requiring official academic record keeping

**OPTIMAL for Canvas:**
- Complex discussions with threading and moderation needs
- High-stakes assessments with robust anti-cheating requirements
- Activities requiring detailed instructor feedback and annotation
- Integration with institutional student information systems

### CourseArc Platform Selection Criteria

**REQUIRED for CourseArc:**
- **WCAG 2.1 Compliance**: Content requiring built-in accessibility features
- **Narrative Control**: Sequential content requiring tight presentation flow
- **Interactive Blocks**: Simple interactions (sorting, matching, flip cards)
- **Professional Aesthetics**: Content requiring polished, modern presentation

**OPTIMAL for CourseArc:**
- Media-heavy presentations with embedded video/audio
- Concept exploration requiring interactive diagrams  
- Welcome/orientation content requiring high engagement
- Bridge content connecting major course sections

## Platform Pros and Cons Analysis

### Canvas Advantages
| Strength | Impact | Use Case |
|----------|---------|----------|
| **Robust Grading Infrastructure** | High | M&M Innovation discussions, comprehensive quizzes |
| **Instructor Workflow Integration** | High | SpeedGrader efficiency, gradebook management |
| **Institutional Data Systems** | High | Official transcripts, compliance reporting |
| **Mature Discussion Threading** | Medium | Complex peer evaluation with multiple reply levels |
| **Anti-Cheating Features** | Medium | High-stakes knowledge assessments |

### Canvas Limitations
| Limitation | Impact | Mitigation Strategy |
|------------|---------|-------------------|
| **Basic Presentation Aesthetics** | Medium | Use CourseArc for content, Canvas for structure |
| **Limited Interactive Elements** | Medium | Embed CourseArc lessons for interactivity |
| **Mobile Experience Gaps** | Low | Responsive design improvements in recent versions |

### CourseArc Advantages  
| Strength | Impact | Use Case |
|----------|---------|----------|
| **Modern "Web-Page" Aesthetics** | High | Professional presentation for physician audience |
| **Built-in WCAG 2.1 Compliance** | High | Accessibility without custom development |
| **Native Interactive Blocks** | High | Concept sorting, idea evaluation exercises |
| **Seamless Media Integration** | Medium | Embedded podcasts, video sequences |
| **Mobile-Optimized Experience** | Medium | Physician on-the-go learning patterns |

### CourseArc Limitations
| Limitation | Impact | Mitigation Strategy |
|------------|---------|-------------------|
| **Limited Grading Infrastructure** | High | Use Canvas for all graded activities |
| **Potential Transition Confusion** | Medium | Consistent styling and clear navigation cues |
| **External Asset Accessibility Risk** | Medium | Audit all Midjourney images and ElevenLabs audio for proper tagging |
| **Click-Level Analytics Complexity** | Low | Use Canvas + CourseArc combination for comprehensive tracking |

## Implementation Guidelines

### Content Allocation Workflow

1. **Primary Assessment**: Does this activity require grading?
   - **YES** → Canvas (unless simple completion tracking)
   - **NO** → Proceed to content type analysis

2. **Social Component Assessment**: Does this require peer interaction?
   - **YES** → Canvas (peer visibility essential)
   - **NO** → Proceed to presentation analysis

3. **Presentation Requirements**: Does this need polished, narrative control?
   - **YES** → CourseArc (modern aesthetics + flow control)
   - **NO** → Canvas (adequate for basic content)

4. **Accessibility Requirements**: Is WCAG 2.1 compliance critical?
   - **YES** → CourseArc (built-in compliance) + accessibility audit
   - **NO** → Either platform acceptable

### Integration Patterns

#### Pattern 1: Canvas Module → CourseArc Lesson
```
Canvas Module Page (structure) 
  → CourseArc Lesson Link (content delivery)
  → Return to Canvas (next activity/discussion)
```

#### Pattern 2: Canvas Discussion + CourseArc Preparation  
```
CourseArc Lesson (concept introduction)
  → Canvas Discussion (peer application/evaluation)
  → Canvas Summary (instructor synthesis)
```

#### Pattern 3: Mixed Assessment Strategy
```
CourseArc Knowledge Check (formative feedback)
  → Canvas Quiz (formal graded assessment)
  → Canvas Grade Passback (official record)
```

### Quality Assurance Standards

#### Visual Consistency Requirements
- **Brand Alignment**: Both platforms use consistent color palette and typography
- **Navigation Clarity**: Clear indicators of platform transitions and return paths  
- **Loading Experience**: Smooth handoffs without jarring interface changes

#### Accessibility Compliance
- **CourseArc Content**: Leverage built-in WCAG 2.1 features
- **External Assets**: All Midjourney images require descriptive alt-text
- **Audio Content**: All ElevenLabs generated audio requires accurate captions
- **Canvas Integration**: Ensure accessibility features work across platform boundaries

#### Data Coherence Standards
- **Grade Passback**: All CourseArc completion data flows to Canvas gradebook
- **Progress Tracking**: Learner progress visible in both platforms consistently  
- **Analytics Reconciliation**: Interaction data from CourseArc supplements Canvas analytics

## Agent Implementation Requirements

### Platform Allocation Agent Capabilities
The automated platform allocation system must:

1. **Parse Content Requirements**: Analyze instructional objectives, interaction patterns, and assessment needs
2. **Apply Decision Framework**: Systematically evaluate Canvas vs CourseArc criteria
3. **Generate Integration Plan**: Specify handoff patterns and data flow requirements
4. **Validate Accessibility**: Ensure WCAG 2.1 compliance across platform boundaries
5. **Document Rationale**: Provide clear reasoning for each allocation decision

### Quality Assurance Agent Capabilities
The platform quality system must:

1. **Audit Transitions**: Detect jarring or confusing platform handoffs
2. **Verify Accessibility**: Confirm proper alt-text, captions, and compliance features
3. **Test User Flow**: Validate smooth navigation and consistent experience
4. **Monitor Analytics**: Track platform-specific engagement and completion metrics
5. **Alert Integration Issues**: Identify grade passback or data synchronization problems

## Policy Evolution Triggers

### Quarterly Review Criteria
- **Platform Feature Updates**: New Canvas or CourseArc capabilities affecting optimal allocation
- **User Experience Metrics**: Learner feedback indicating transition confusion or platform preferences  
- **Instructor Workflow Changes**: Faculty efficiency impacts from allocation decisions
- **Accessibility Compliance Updates**: WCAG guideline changes or institutional requirements

### Emergency Policy Updates
- **Critical Accessibility Issues**: Immediate compliance problems requiring reallocation
- **Platform Outages**: Contingency allocation when primary platform unavailable
- **Security Concerns**: Data protection issues requiring platform usage changes
- **Institutional Policy Changes**: LMS requirements from university administration

## Success Metrics

### Learner Experience
- **Completion Rates**: >90% across both platforms
- **Transition Confusion**: <10% reporting navigation difficulties  
- **Engagement Metrics**: Platform-appropriate interaction levels
- **Accessibility Usage**: WCAG feature utilization tracking

### Instructor Efficiency  
- **SpeedGrader Usage**: Efficient grading workflow maintenance
- **Discussion Management**: Effective peer learning facilitation
- **Administrative Load**: Minimal platform switching overhead
- **Analytics Utility**: Actionable insights from combined platform data

### Technical Performance
- **Platform Integration**: Seamless grade passback and data flow
- **Accessibility Compliance**: 100% WCAG 2.1 adherence verification
- **Mobile Performance**: Consistent experience across devices  
- **Loading Performance**: <3 second transitions between platforms

This policy ensures optimal platform utilization while maintaining flexibility for course-specific needs and emerging technological capabilities.
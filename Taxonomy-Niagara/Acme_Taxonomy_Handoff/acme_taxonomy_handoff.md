
# Acme Taxonomy Master Handoff (Markdown Full Version)

## Purpose
This file contains the full grounding content needed for Copilot and for project onboarding. It includes summaries of the folder structure, taxonomy purpose, crosswalk logic, governance, automation, and restart instructions.

## 1. Executive Summary
The Acme Enterprise Taxonomy defines a unified, governed metadata structure for all products, documents, features, and content types across Acme’s ecosystem. It improves tagging accuracy, search relevance, analytics, and documentation consistency.

## 2. Folder Structure (Authoritative Version)
```
Acme_Taxonomy_Project/
│
├── 00_Project_HandOff/
├── 01_Taxonomy_Definition/
├── 02_Data_Inputs/
├── 03_Scripts/
├── 04_Deliverables/
└── 05_Archive/
```

## 3. Essential Definitions
### Product Taxonomy
A hierarchical model organizing Acme's product ecosystem into:  
- Supervisor  
- Cloud Suite  
- Analytics  
- Enterprise Security  
- Drivers  
- Hardware Controllers  
- I/O Modules  

### Document Taxonomy
Organizes content by purpose, audience, and type.

### Controlled Vocabulary
Defines canonical names, synonyms, preferred terms, and alternate label sets.

## 4. Crosswalk Strategy
Crosswalks connect Product Taxonomy → Document Taxonomy → Functional Tags.  
They ensure consistent tagging, analytics alignment, and metadata interoperability.

## 5. Governance Model
Changes move through: request → SME review → writer integration → approval → release.  
Roles include Technical Writers, Product Marketing, Engineering SMEs, and Taxonomy Stewards.

## 6. Automation Overview
Python scripts import corporate spreadsheets, resolve names to taxonomy IDs, validate anomalies, and output standardized tables for publishing.

## 7. Restart Kit (AI Session Initialization)
When beginning a new Copilot session, use:
```
You are working with the Acme Enterprise Taxonomy. Load the folder:
Acme_Taxonomy_Project/00_Project_HandOff
and ground your reasoning in all files in that folder. The master handoff file is:
acme_taxonomy_handoff.md
Respond with summaries, validations, and taxonomy operations.
```

## 8. First Message for Copilot
“Copilot, load the entire folder *00_Project_HandOff* and use all documents within it as grounding context. This includes the Master Project Summary, Terms & Data Dictionary, Product Taxonomy Outline, Document Taxonomy Outline, Crosswalk Strategy, Governance Model, Python Script Architecture, Restart Kit, and this Markdown file. After loading them, acknowledge readiness.”

## 9. One-Page Visual Summary (Text Version)
```
PRODUCT TAXONOMY
   → DOCUMENT TAXONOMY
       → CONTROLLED VOCAB
           → CROSSWALK (Products ↔ Docs ↔ Tags)
               → AUTOMATION (Mapping Scripts)
                   → RELEASE & GOVERNANCE
```

## 10. Copilot Usage Guide (Quick Start)
- Ask Copilot to classify new products.  
- Ask Copilot to generate crosswalks.  
- Ask Copilot to validate taxonomy consistency.  
- Ask Copilot to analyze spreadsheets for unrecognized terms.  
- Ask Copilot to clean metadata and propose canonical forms.  
- Use Copilot to draft new taxonomy releases (v1, v2…).

This file is complete and intended for immediate use.

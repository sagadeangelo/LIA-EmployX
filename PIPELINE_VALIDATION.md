# Pipeline Validation Matrix

**Status:** Failed at the first loss boundary. Later stages were intentionally not executed.

| Required check | Status | Evidence |
| --- | --- | --- |
| raw text extracted | Pass | DOCXLoader extracted 6,624 characters. |
| sections populated | **Fail** | Seven of eight sections are empty; the full normalized CV is one experience block. |
| ExperienceBuilder creates `CVExperience` objects | Diagnostic only | One object from the incorrectly merged 6,344-character block. |
| EducationBuilder creates `CVEducation` objects | Not valid | Empty section input produces zero objects. |
| LanguagesBuilder creates `CVLanguage` objects | Not valid | Empty section input produces zero objects. |
| SkillsBuilder creates structured skills | Not valid | Empty section input produces zero objects. |
| ProfessionalProfile contains real data | Not executed | Blocked by invalid CVDocument. |
| `profiles.json` persists all collections | Not executed | No invalid audit profile was saved. |
| `GET /profile/{id}` returns collections | Not executed | No profile ID was created. |
| Flutter renders populated values | Not executed | No valid API payload exists. |

## Test gate

No end-to-end test was added or updated after the failure because the stop condition was reached. After the documented correction is approved, the first required regression test must assert that this exact DOCX produces non-empty `personal_info`, `experience`, `education`, `skills`, `languages`, and `certifications` sections before builder, repository, API, or Flutter assertions run.

The root cause and non-implemented correction proposal are documented in `ROOT_CAUSE_STAGE_DOCX_LOADER.md`.

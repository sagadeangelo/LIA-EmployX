import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute()))

from backend.modules.cv.services.extraction_service import ExtractionService
from backend.modules.cv.mappers.professional_profile_mapper import ProfessionalProfileMapper
from backend.modules.profile.repositories.profile_repository import ProfileRepository

def safe(s): return str(s).encode('ascii', errors='replace').decode('ascii')

CV_PATH = r'D:\PROYECTOS_FLUTTER\lia-employx\data\uploads\5caccf4a7aa9483db0427c1186818e00_CV_Miguel_Tovar_Full_Stack_English.docx'

# 1. Run full extraction pipeline
print('=== STEP 1: ExtractionService.process() ===')
svc = ExtractionService()
cv_doc = svc.process(CV_PATH)

print(safe(f'Experiences  : {len(cv_doc.experiences)}'))
print(safe(f'Education    : {len(cv_doc.education)}'))
print(safe(f'Skills       : {len(cv_doc.skills)}'))
print(safe(f'Languages    : {len(cv_doc.languages)}'))
print(safe(f'Certifications: {len(cv_doc.certifications)}'))
print(safe(f'Summary      : {cv_doc.professional_summary[:80] if cv_doc.professional_summary else "(empty)"}'))
print(safe(f'Contact name : {cv_doc.contact.name if cv_doc.contact else "(none)"}'))

# 2. Map to ProfessionalProfile
print('\n=== STEP 2: ProfessionalProfileMapper ===')
profile = ProfessionalProfileMapper.from_cv_document(cv_doc)

print(safe(f'Profile ID   : {profile.id}'))
print(safe(f'Experiences  : {len(profile.experiences)}'))
print(safe(f'Education    : {len(profile.education)}'))
print(safe(f'Skills       : {len(profile.skills)}'))
print(safe(f'Languages    : {len(profile.languages)}'))

for exp in profile.experiences:
    c = getattr(exp, 'company', '?')
    p = getattr(exp, 'position', '?')
    print(safe(f'  EXP: {c} | {p}'))

# 3. Persist to ProfileRepository
print('\n=== STEP 3: ProfileRepository.save() ===')
repo = ProfileRepository()
saved = repo.save(profile)
print(safe(f'Saved: {saved}'))

# 4. Reload and verify
loaded = repo.get_by_id(profile.id)
if loaded:
    print(safe(f'Reloaded profile OK! ID match: {loaded.id == profile.id}'))
    print(safe(f'Reloaded experiences: {len(loaded.experiences)}'))
else:
    print('ERROR: failed to reload profile from repository.')

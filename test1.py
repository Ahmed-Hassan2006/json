import os
import requests
import re

# 1. إعداد المجلد الرئيسي الذي سيتم حفظ كل شيء فيه للعبتك
BASE_DIR = "Offline_Game_Databases"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# 2. قائمة المصادر العربية (المستودعات التي ذكرناها)
REPOS = [
    {"owner": "rn0x", "repo": "IslamicQuizAPI"},
    {"owner": "EmanElrefai", "repo": "AAQAD"},
    {"owner": "Faris-abukhader", "repo": "-JSON-"},
    {"owner": "WissamAntoun", "repo": "Arabic_QA_Datasets"}
]

# دالة لجلب شجرة الملفات من جيت هب تلقائياً لمعرفة الملفات الرئيسية
def get_json_files_from_repo(owner, repo):
    branches = ['main', 'master'] # نجرب المسارين المعتادين
    for branch in branches:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        response = requests.get(api_url)
        if response.status_code == 200:
            tree = response.json().get('tree', [])
            # تصفية الملفات لتشمل قواعد البيانات فقط
            files = [item['path'] for item in tree if item['path'].endswith('.json') or item['path'].endswith('.csv')]
            return files, branch
    return [], None

# دالة لتحميل الملفات وحفظها
def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"✅ تم تحميل: {os.path.basename(save_path)}")
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ خطأ أثناء التحميل: {e}")
        return False

# دالة لفحص الروابط داخل الملفات المحملة وتنزيل الملفات المرتبطة (كما طلبت)
def scan_and_download_links(file_path, folder_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # البحث عن أي رابط داخل النص ينتهي بصيغة ملف بيانات
        urls = re.findall(r'https?://[^\s"\'\]\)]+\.(?:json|csv|txt)', content)
        
        for i, url in enumerate(urls):
            file_name = f"Link_{i}_{os.path.basename(url)}"
            save_path = os.path.join(folder_path, file_name)
            if not os.path.exists(save_path):
                print(f"🔍 تم العثور على رابط لملف خارجي داخل النص! جاري سحبه: {url}")
                download_file(url, save_path)
    except Exception:
        pass # تجاهل الملفات التي لا يمكن قراءتها كنص عادي

# --- بداية تشغيل الأداة ---
print("🚀 بدء تشغيل أداة سحب قواعد بيانات الأسئلة العربية لتعمل بدون إنترنت (Offline)...\n")

for repo_info in REPOS:
    owner = repo_info["owner"]
    repo = repo_info["repo"]
    print(f"📦 جاري فحص مصدر الأسئلة: {repo}...")
    
    # إنشاء مجلد خاص بهذا المصدر
    repo_folder = os.path.join(BASE_DIR, repo)
    if not os.path.exists(repo_folder):
        os.makedirs(repo_folder)
        
    # جلب مسارات الملفات من المصدر
    files, branch = get_json_files_from_repo(owner, repo)
    
    if not files:
        print(f"⚠️ تعذر العثور على ملفات في {repo}.\n")
        continue
        
    for file_path in files:
        # تجاهل ملفات النظام والبرمجة التي لا تحتوي على أسئلة
        if "package.json" in file_path or "package-lock.json" in file_path:
            continue
            
        # تجهيز الرابط المباشر (Raw) للتحميل
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
        
        # تجهيز اسم الملف وتجنب المجلدات الفرعية المعقدة لتكون كلها أمامك
        safe_filename = file_path.replace("/", "_") 
        save_path = os.path.join(repo_folder, safe_filename)
        
        # تحميل الملف الأساسي
        if download_file(raw_url, save_path):
            # فحص الملف لتنزيل أي روابط داخله
            scan_and_download_links(save_path, repo_folder)
    print("-" * 40)

print("\n🎉 انتهت العملية بنجاح! افتح مجلد (Offline_Game_Databases) وستجد كل الملفات جاهزة ومقسمة لمسارات لتضعها في لعبتك مباشرة.")
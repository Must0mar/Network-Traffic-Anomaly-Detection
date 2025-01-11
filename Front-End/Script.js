



let emailList = [];

// API URLs (replace with your actual host URL)
const API_GET_URL = "http://192.168.57.9:8080/emails";
const API_POST_URL = "http://192.168.57.9:8080/emails"; 

const API_GET_ALERT = "http://192.168.57.9:8080/alert";
let englishAlertInst = "";
let kurdishAlertInst = "";
let arabicAlertInst = "";



// Function to fetch the email list from the API
async function fetchEmailList() {
    try {
        const response = await fetch(API_GET_URL);
        if (!response.ok) {
            throw new Error(`Failed to fetch emails: ${response.statusText}`);
        }
        const data = await response.json(); // Fetch the entire response
        emailList = data.emails; // Extract the emails array
        if (!Array.isArray(emailList)) {
            throw new Error("Invalid data format: 'emails' should be an array.");
        }
        renderEmailList(); // Render the list only if it's valid
    } catch (error) {
        console.error(error);
    }
}


// Function to render the email list in the UI
function renderEmailList() {
    const emailListContainer = document.querySelector('.email-list');
    emailListContainer.innerHTML = '';
    emailList.forEach((email, index) => {
        const emailItem = document.createElement('div');
        emailItem.className = 'email-item';
        emailItem.innerHTML = `
            <input type="text" value="${email}" data-index="${index}" onchange="updateEmail(event)" />
            <button onclick="removeEmail(${index})">Delete</button>
        `;
        emailListContainer.appendChild(emailItem);
    });
}

// Function to handle email updates
function updateEmail(event) {
    const index = event.target.dataset.index;
    emailList[index] = event.target.value;
}

// Function to add a new email
function AddEmail() {
    const newEmail = prompt("Enter a new email:");
    if (newEmail) {
        emailList.push(newEmail);
        renderEmailList();
    }
}

// Function to remove an email
function removeEmail(index) {
    emailList.splice(index, 1);
    renderEmailList();
}

// Function to save the email list back to the API
async function saveEmailList() {
    try {
        const response = await fetch(API_POST_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ emails: emailList }), // Wrap emailList in an object
        });
        if (!response.ok) {
            throw new Error(`Failed to save emails: ${response.statusText}`);
        }
        alert("Email list saved successfully!");
    } catch (error) {
        console.error(error);
    }
}


// Function to cancel editing (reloads the list from the API)
function cancelEditing() {
    fetchEmailList();
}

// Initial fetch of the email list
document.addEventListener('DOMContentLoaded', fetchEmailList);

// URL for the GET request (replace with the actual API endpoint)
const API_URL = "http://192.168.57.9:8080/get-data";


// Function to fetch data from the API
async function fetchAnomalyData() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`Failed to fetch data: ${response.statusText}`);
        }
        const data = await response.json();
        updateUI(data);
        toggleMessage(data.total_anomalies >0);
        // loadAlertInstructions();
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

// Function to load alert instructions
// async function loadAlertInstructions() {
//     try {
//         const response = await fetch(API_GET_ALERT);
//         if (!response.ok) {
//             throw new Error('Failed to fetch alert instructions');
//         }
//         const alertData = await response.json();
        
//         // Get the current language (default to English if not set)
//         const currentLang = localStorage.getItem("selectedLanguage") || "en";
        
//         // Update the message content
//         const messageElement = document.querySelector('.message p');
//         if (messageElement) {
//             messageElement.textContent = alertData[currentLang] || alertData['en'];
//         }
//     } catch (error) {
//         console.error('Error loading alert instructions:', error);
        
//         // Fallback message if JSON loading fails
//         const messageElement = document.querySelector('.message p');
//         if (messageElement) {
//             messageElement.textContent = "An error occurred while loading alert instructions.";
//         }
//     }
// }

async function loadAlertInstructions() {
    try {
        const response = await fetch(API_GET_ALERT);
        if (!response.ok) {
            throw new Error('Failed to fetch alert instructions');
        }
        const alertData = await response.json();
        
        // Store alert instructions in respective language variables
        englishAlertInst = alertData['en'] || "No English instructions available.";
        kurdishAlertInst = alertData['ku'] || "No Kurdish instructions available.";
        arabicAlertInst = alertData['ar'] || "No Arabic instructions available.";
        
        // Get the current language (default to English if not set)
        const currentLang = localStorage.getItem("selectedLanguage") || "en";
        
        // Update the message content based on current language
        const messageElement = document.querySelector('.message p');
        if (messageElement) {
            switch(currentLang) {
                case 'ku':
                    messageElement.textContent = kurdishAlertInst;
                    break;
                case 'ar':
                    messageElement.textContent = arabicAlertInst;
                    break;
                default:
                    messageElement.textContent = englishAlertInst;
            }
        }
    } catch (error) {
        console.error('Error loading alert instructions:', error);
        
        // Fallback message if JSON loading fails
        const messageElement = document.querySelector('.message p');
        if (messageElement) {
            messageElement.textContent = "An error occurred while loading alert instructions.";
        }
    }
}

// Modify the existing toggleMessage function
function toggleMessage(show) {
    const messageElement = document.querySelector('.message');
    if (show) {
        messageElement.style.display = 'block'; // Show the alert message
        // loadAlertInstructions(); // Load and update instructions
    } else {
        messageElement.style.display = 'none'; // Hide the alert message
    }
}

// Function to update the UI with fetched data
function updateUI(data) {
    // Update Total Packets
    document.getElementById("total-packets").textContent = data.total_packets;

    // Update Protocol Distribution
    const protocolDetails = document.getElementById("protocol-details");
    protocolDetails.innerHTML = ""; // Clear existing content
    for (const [protocol, count] of Object.entries(data.protocol_distribution)) {
        const detail = document.createElement("p");
        detail.textContent = `${protocol}: ${count}`;
        protocolDetails.appendChild(detail);
    }

    // Update Total Anomalies
    document.getElementById("total-anomalies").textContent = data.total_anomalies;

    // Update Anomalies Details
    const anomaliesDetails = document.getElementById("anomalies-details");
    anomaliesDetails.innerHTML = ""; // Clear existing content
    for (const [type, count] of Object.entries(data.anomalies_by_type)) {
        const detail = document.createElement("p");
        if (type==1){
            attackType ="Port Scanning";
        }else if(type==2){
            attackType ="DOS Attacking";
        }else{
            attackType ="Others";
        }
        detail.textContent = `${attackType}: ${count}`;
        anomaliesDetails.appendChild(detail);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    fetchAnomalyData(); // Initial fetch
    loadAlertInstructions();
    setInterval(fetchAnomalyData, 2000);
    setInterval(loadAlertInstructions, 2000); 
});

// Translation data
const translations = {
    en: {
        "email-settings": "Email Settings",
        "title": "Network Anomaly Detection System",
        "welcome": "Welcome to the Home Network Traffic Anomaly Detection System",
        "intro": "This system is designed to ensure the security and reliability of your home network. It uses a trained machine learning model to monitor network traffic in real-time and detect anomalies or potential attacks.",
        "email-notification": "As soon as an anomaly is detected, the system will automatically send an email notification to the user. The email will include detailed information about the detected attack and specific instructions on how to respond to the threat effectively.",
        "explore-dashboard": "Explore the dashboard to view key metrics such as total network packets, protocol distribution, and details about detected anomalies. Use the email settings to customize notifications and stay informed about the security status of your home network.",
        "packets": "Packets",
        "protocol-distribution": "Protocol Distribution",
        "total-anomalies": "Total Anomalies",
        "anomalies": "Anomalies by Type",
        "back": "Back",
        "title": "Network Anomaly Detection System",
        "email-list": "Email List",
        "save": "Save",
        "add": "Add",
        "cancel": "Cancel"
    },
    ku: {
        "email-settings": "ڕێکخستنەکانی ئیمەیڵ",
        "title": "سیستەمی دۆزینەوەی ڕەفتارە نائاساییەکانی تۆڕ",
        "welcome": "بەخێربێن بۆ سیستەمی چاودێری ڕەفتارە نائاساییەکانی تۆڕی ماڵەوە",
        "intro": "ئەم سیستەمە بۆ پاراستن و دڵنیایی تۆڕی ماڵەوەت داڕێژراوە. ئەو بەرنامە هۆشمەندەیە کە ڕاهاتووە بۆ چاودێریکردنی هاتووچۆی تۆڕ بە شێوەیەکی ڕاستەوخۆ و دۆزینەوەی هەر ڕەفتارێکی گومانلێکراو یان هەڕەشەیەکی ئەگەری.",
        "email-notification": "هەر کاتێک ڕەفتارێکی گومانلێکراو دۆزرایەوە، سیستەمەکە بە شێوەیەکی خۆکار ناردنی ئیمەیڵی ئاگادارکردنەوە دەکات. ئیمەیڵەکە وردەکاریی تەواوی ڕەفتارە گومانلێکراوەکە و ڕێنمایی ڕوون دەگرێتەوە کە چۆن بەرەنگاری هەڕەشەکە ببیتەوە بە شێوەیەکی سەلامەت.",
        "explore-dashboard": "پانێڵی بەڕێوەبەری بکەوە بۆ بینینی پێوەرە سەرەکیەکان وەک ژمارەی پاکێتەکان، دابەشبوونی جۆرەکانی پەیوەندی، و وردەکاریی ڕەفتارە نائاساییەکان. ڕێکخستنەکانی ئیمەیڵ بەکاربهێنە بۆ ئاراستەکردنی ئاگادارکردنەوەکان و لە بارودۆخی پاراستنی تۆڕی ماڵەوەتدا بمێنەوە.",
        "packets": "پاکێتەکان",
        "protocol-distribution": "دابەشبوونی جۆرەکانی پەیوەندی",
        "total-anomalies": "کۆی ڕەفتارە گومانلێکراوەکان",
        "anomalies": "جۆرەکانی ڕەفتارە گومانلێکراوەکان",
        "back": "گەڕانەوە",
        "title": "سیستەمی دۆزینەوەی شێوانەی تور",
        "email-list": "لیستی ئیمەیڵ",
        "save": "پاشەکەوت",
        "add": "زیادکردن",
        "cancel": "هەڵوەشاندنەوە"

    },
    ar: {
        "email-settings": "إعدادات البريد الإلكتروني",
        "title": "نظام كشف الأنشطة الغير طبيعية في الشبكة",
        "welcome": "أهلاً بك في نظام مراقبة الأنشطة غير العادية في شبكة المنزل",
        "intro": "تم تطوير هذا النظام لحماية شبكة المنزل وضمان أمنها. يعتمد على برنامج ذكي متدرب على مراقبة حركة الشبكة بشكل مباشر واكتشاف أي نشاط مشبوه أو هجمات محتملة.",
        "email-notification": "فور اكتشاف أي نشاط مريب، سيرسل النظام تلقائياً رسالة تنبيه إلى بريدك الإلكتروني. ستحتوي الرسالة على تفاصيل كاملة عن النشاط المشبوه وتعليمات واضحة لكيفية التعامل مع التهديد بشكل آمن.",
        "explore-dashboard": "تصفح لوحة المعلومات لمشاهدة المؤشرات الرئيسية مثل عدد حزم البيانات، توزيع أنواع الاتصالات، وتفاصيل الأنشطة غير الطبيعية. استخدم إعدادات البريد الإلكتروني لتخصيص التنبيهات والبقاء على اطلاع بحالة أمن شبكة المنزل.",
        "packets": "الحزم",
        "protocol-distribution": "توزيع أنواع الاتصالات",
        "total-anomalies": "إجمالي الأنشطة المشبوهة",
        "anomalies": "نوع الأنشطة المشبوهة",
        "back": "الرجوع",
        "title": "نظام كشف الشذوذ في الشبكة",
        "email-list": "قائمة البريد الإلكتروني",
        "save": "حفظ",
        "add": "إضافة",
        "cancel": "إلغاء"
   
    }
};

function changeLanguage(lang) {
    localStorage.setItem("selectedLanguage", lang); // Save language to localStorage
    document.querySelectorAll("[data-key]").forEach((element) => {
        const key = element.getAttribute("data-key");
        if (translations[lang] && translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });

    const messageElement = document.querySelector('.message p');
    if (messageElement) {
        switch(lang) {
            case 'ku':
                messageElement.textContent = kurdishAlertInst;
                break;
            case 'ar':
                messageElement.textContent = arabicAlertInst;
                break;
            default:
                messageElement.textContent = englishAlertInst;
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const savedLanguage = localStorage.getItem("selectedLanguage") || "en"; // Default to English
    changeLanguage(savedLanguage);
});

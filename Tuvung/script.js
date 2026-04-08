const API_URL = "http://127.0.0.1:8888";
let authToken = "";
let savedWordsData = []; // Biến tạm lưu danh sách từ để làm Quiz

// 1. Đăng ký & Đăng nhập (Giữ nguyên như cũ)
async function register() { /* ... như cũ ... */ }
async function login() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    try {
        const response = await fetch(`${API_URL}/api/auth/login`, { method: 'POST', body: formData });
        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            document.getElementById('auth-section').classList.add('d-none');
            document.getElementById('main-app').classList.remove('d-none');
            document.getElementById('user-display').innerText = email;
            loadSavedWords();
        } else { alert("Sai thông tin!"); }
    } catch (e) { alert("Lỗi kết nối!"); }
}

// 2. PHÁT ÂM (Tính năng 1)
// Hàm phát âm thanh chuẩn xác
function speak(word) {
    if (!word) return;

    // 1. Kiểm tra xem trình duyệt có hỗ trợ bộ đọc không
    if (!window.speechSynthesis) {
        alert("Trình duyệt của bạn không hỗ trợ phát âm!");
        return;
    }

    // 2. Hủy các yêu cầu đọc đang dang dở (để không bị nói chồng lên nhau)
    window.speechSynthesis.cancel();

    // 3. Tạo một yêu cầu đọc mới
    const utterance = new SpeechSynthesisUtterance(word);

    // 4. Thiết lập ngôn ngữ là tiếng Anh (Mỹ hoặc Anh tùy máy)
    utterance.lang = 'en-US';
    utterance.rate = 0.9; // Đọc chậm lại một chút cho dễ nghe
    utterance.pitch = 1;  // Cao độ vừa phải

    // 5. Thực hiện đọc
    window.speechSynthesis.speak(utterance);

    // Xử lý lỗi im lặng trên một số trình duyệt mobile/đặc biệt
    utterance.onerror = (event) => {
        console.error("Lỗi phát âm:", event.error);
    };
}

// 3. Tìm kiếm (Thêm nút loa)
async function searchWord() {
    const keyword = document.getElementById('search-input').value;
    const resultDiv = document.getElementById('search-result');
    resultDiv.innerHTML = '<div class="text-center my-4"><div class="spinner-border text-primary"></div></div>';

    try {
        const response = await fetch(`${API_URL}/api/vocab/search?keyword=${keyword}`);
        const data = await response.json();
        let html = '';
        data.forEach(vocab => {
            const img = vocab.image_url || `https://ui-avatars.com/api/?name=${vocab.word}&background=random`;
            html += `
            <div class="card vocab-card p-3 mb-3 shadow-sm border-0 border-start border-5 border-primary">
                <div class="row align-items-center">
                    <div class="col-md-3 text-center"><img src="${img}" class="img-fluid rounded shadow-sm" style="height:120px; width:100%; object-fit:cover;"></div>
                    <div class="col-md-9">
                        <div class="d-flex justify-content-between">
                            <h4 class="text-primary">${vocab.word}
                                <button onclick="speak('${vocab.word}')" class="btn btn-sm btn-light">🔊</button>
                            </h4>
                            <button onclick="saveWord(${vocab.id})" class="btn btn-outline-success btn-sm">⭐ Lưu</button>
                        </div>
                        <p class="fw-bold mb-1">${vocab.meaning}</p>
                        <div class="text-muted fst-italic">"${vocab.example_sentence}"</div>
                    </div>
                </div>
            </div>`;
        });
        resultDiv.innerHTML = html;
    } catch (e) { resultDiv.innerHTML = 'Lỗi!'; }
}

// 4. XÓA TỪ (Tính năng 2)
async function deleteWord(vocabId) {
    if(!confirm("Bạn muốn xóa từ này khỏi sổ tay?")) return;
    try {
        const response = await fetch(`${API_URL}/api/vocab/delete/${vocabId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) { loadSavedWords(); }
    } catch (e) { alert("Lỗi xóa từ!"); }
}

// 5. Tải sổ tay (Thêm nút xóa và loa)
async function loadSavedWords() {
    const savedListDiv = document.getElementById('saved-list');
    try {
        const response = await fetch(`${API_URL}/api/vocab/saved`, { headers: { 'Authorization': `Bearer ${authToken}` } });
        savedWordsData = await response.json();
        let html = '';
        savedWordsData.forEach(vocab => {
            const img = vocab.image_url || `https://ui-avatars.com/api/?name=${vocab.word}&background=random`;
            html += `
            <div class="col-md-6 mb-4">
                <div class="card h-100 border-0 shadow-sm border-bottom border-4 border-success">
                    <img src="${img}" class="card-img-top" style="height:150px; object-fit:cover;">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <h5 class="text-success">${vocab.word} <button onclick="speak('${vocab.word}')" class="btn btn-sm btn-light">🔊</button></h5>
                            <button onclick="deleteWord(${vocab.id})" class="btn btn-sm text-danger">🗑️</button>
                        </div>
                        <p class="fw-bold">${vocab.meaning}</p>
                    </div>
                </div>
            </div>`;
        });
        savedListDiv.innerHTML = html || '<p class="text-muted p-3">Chưa có từ nào.</p>';
    } catch (e) { }
}

// 6. ÔN TẬP FLASHCARD (Tính năng 3)
function startQuiz() {
    if (savedWordsData.length < 2) {
        alert("Bạn cần lưu ít nhất 2 từ để bắt đầu ôn tập!");
        return;
    }
    const container = document.getElementById('quiz-container');
    const randomVocab = savedWordsData[Math.floor(Math.random() * savedWordsData.length)];

    container.innerHTML = `
        <div class="bg-white text-dark p-4 rounded shadow-lg animate__animated animate__flipInX">
            <h2 class="display-4 text-primary fw-bold">${randomVocab.word}</h2>
            <p class="text-muted mb-4">Từ này có nghĩa là gì?</p>
            <div id="quiz-options" class="d-grid gap-2">
                <button onclick="checkAnswer(true, '${randomVocab.word}')" class="btn btn-outline-primary py-2">Xem đáp án</button>
            </div>
            <button onclick="startQuiz()" class="btn btn-link mt-3 text-muted">Bỏ qua từ này ⏭️</button>
        </div>
    `;
}

function checkAnswer(show, correctWord) {
    const vocab = savedWordsData.find(v => v.word === correctWord);
    const container = document.getElementById('quiz-container');
    container.innerHTML = `
        <div class="bg-white text-dark p-4 rounded shadow-lg border-start border-5 border-success">
            <h4 class="text-success">Đáp án chính xác!</h4>
            <h2 class="text-primary">${vocab.word}</h2>
            <hr>
            <p class="fs-5 fw-bold">${vocab.meaning}</p>
            <p class="fst-italic">"${vocab.example_sentence}"</p>
            <button onclick="speak('${vocab.word}')" class="btn btn-warning me-2">Nghe lại 🔊</button>
            <button onclick="startQuiz()" class="btn btn-primary px-4">Từ tiếp theo ➡️</button>
        </div>
    `;
}
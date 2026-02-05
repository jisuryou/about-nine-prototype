const API_BASE = `${window.location.origin}/api`;

// API 호출 헬퍼
async function apiCall(endpoint, method = 'GET', data = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // 세션 쿠키 포함
  };
  
  if (data && method !== 'GET') {
    options.body = JSON.stringify(data);
  }
  
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.message || '요청 실패');
    }
    
    return result;
  } catch (error) {
    console.error('API 호출 오류:', error);
    throw error;
  }
}

// 로컬 스토리지 헬퍼
function saveToLocal(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error('localStorage 저장 오류:', error);
  }
}

function getFromLocal(key) {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  } catch (error) {
    console.error('localStorage 읽기 오류:', error);
    return null;
  }
}

function removeFromLocal(key) {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('localStorage 삭제 오류:', error);
  }
}

// 페이지 이동
function navigateTo(page) {
  window.location.href = page;
}

// 로딩 표시
function showLoading(text = '처리 중...') {
  let overlay = document.getElementById('loading-overlay');
  
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.innerHTML = `
      <div class="loading-asterisks">
        <img src="images/asterisk.png" class="asterisk asterisk-1" alt="loading">
        <img src="images/asterisk.png" class="asterisk asterisk-2" alt="loading">
      </div>
      <div class="loading-text">${text}</div>
    `;
    document.body.appendChild(overlay);
  } else {
    overlay.querySelector('.loading-text').textContent = text;
    overlay.classList.remove('hidden');
  }
}

function hideLoading() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.classList.add('hidden');
  }
}

// 에러 메시지 표시
function showError(elementId, message) {
  const errorDiv = document.getElementById(elementId);
  if (errorDiv) {
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
  }
}

function hideError(elementId) {
  const errorDiv = document.getElementById(elementId);
  if (errorDiv) {
    errorDiv.textContent = '';
    errorDiv.classList.add('hidden');
  }
}

// 유틸리티 함수들
function formatPhoneNumber(value) {
  // 숫자만 추출
  const numbers = value.replace(/[^0-9]/g, '');
  
  // 010-1234-5678 형식으로 변환
  if (numbers.length <= 3) {
    return numbers;
  } else if (numbers.length <= 7) {
    return numbers.slice(0, 3) + '-' + numbers.slice(3);
  } else {
    return numbers.slice(0, 3) + '-' + numbers.slice(3, 7) + '-' + numbers.slice(7, 11);
  }
}

function calculateAge(birthDate) {
  const birth = new Date(birthDate);
  const today = new Date();
  const age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    return age - 1;
  }
  
  return age;
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
  console.log('Common.js 로드 완료');
});
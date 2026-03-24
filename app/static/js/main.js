// 네이버 부동산 크롤링 서비스 JavaScript

class RealEstateApp {
    constructor() {
        this.map = null;
        this.markers = [];
        this.selectedLocations = [];
        this.properties = [];
        
        this.init();
    }
    
    init() {
        this.initMap();
        this.setupEventListeners();
        this.loadInitialData();
    }
    
    initMap() {
        // 서울 중심으로 지도 초기화
        this.map = L.map('map').setView([37.5665, 126.9780], 11);
        
        // OpenStreetMap 타일 레이어 추가
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(this.map);
        
        // 지도 클릭 이벤트
        this.map.on('click', (e) => {
            this.addLocationFromMap(e.latlng);
        });
    }
    
    setupEventListeners() {
        // 검색 버튼
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.searchProperties());
        }
        
        // 지역 입력
        const locationInput = document.getElementById('location-input');
        if (locationInput) {
            locationInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.addLocation();
            });
        }
        
        // 지역 추가 버튼
        const addLocationBtn = document.getElementById('add-location-btn');
        if (addLocationBtn) {
            addLocationBtn.addEventListener('click', () => this.addLocation());
        }
        
        // 내보내기 버튼
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }
    }
    
    loadInitialData() {
        // 초기 통계 데이터 로드
        this.updateStats();
        
        // 로컬 스토리지에서 저장된 설정 로드
        this.loadSettings();
    }
    
    addLocation() {
        const input = document.getElementById('location-input');
        const location = input.value.trim();
        
        if (location && !this.selectedLocations.includes(location)) {
            this.selectedLocations.push(location);
            this.updateLocationDisplay();
            input.value = '';
        }
    }
    
    addLocationFromMap(latlng) {
        // 간단한 좌표를 지역명으로 변환 (실제 구현에서는 역지오코딩 필요)
        const locationName = `위도: ${latlng.lat.toFixed(4)}, 경도: ${latlng.lng.toFixed(4)}`;
        
        if (!this.selectedLocations.includes(locationName)) {
            this.selectedLocations.push(locationName);
            this.updateLocationDisplay();
            
            // 마커 추가
            const marker = L.marker([latlng.lat, latlng.lng]).addTo(this.map);
            marker.bindPopup(`<b>${locationName}</b>`).openPopup();
            this.markers.push(marker);
        }
    }
    
    updateLocationDisplay() {
        const container = document.getElementById('selected-locations');
        if (!container) return;
        
        container.innerHTML = this.selectedLocations.map(loc => `
            <span class="location-tag">
                ${loc}
                <button onclick="app.removeLocation('${loc}')">&times;</button>
            </span>
        `).join('');
        
        // 통계 업데이트
        this.updateStats();
    }
    
    removeLocation(location) {
        this.selectedLocations = this.selectedLocations.filter(loc => loc !== location);
        this.updateLocationDisplay();
        
        // 해당 마커 제거
        this.markers.forEach((marker, index) => {
            if (marker.getPopup().getContent().includes(location)) {
                this.map.removeLayer(marker);
                this.markers.splice(index, 1);
            }
        });
    }
    
    async searchProperties() {
        if (this.selectedLocations.length === 0) {
            this.showAlert('검색할 지역을 선택해주세요.', 'warning');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/v1/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    locations: this.selectedLocations
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.properties = data.properties || [];
                this.displayProperties();
                this.updateStats();
            } else {
                this.showAlert(data.message || '검색에 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('검색 오류:', error);
            this.showAlert('검색 중 오류가 발생했습니다.', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    displayProperties() {
        const container = document.getElementById('property-list');
        if (!container) return;
        
        if (this.properties.length === 0) {
            container.innerHTML = '<p>검색 결과가 없습니다.</p>';
            return;
        }
        
        container.innerHTML = this.properties.map(property => `
            <div class="property-card">
                <h3 class="property-title">${property.title}</h3>
                <p class="property-location">${property.location}</p>
                <p class="property-price">${this.formatPrice(property.price)}</p>
                <p class="property-area">${property.area}㎡</p>
                <p>${property.description}</p>
                <a href="${property.url}" target="_blank">원문 보기</a>
            </div>
        `).join('');
    }
    
    formatPrice(price) {
        if (price >= 10000) {
            const 억 = Math.floor(price / 10000);
            const 만 = price % 10000;
            return 만 > 0 ? `${억}억 ${만}만원` : `${억}억원`;
        } else {
            return `${price}만원`;
        }
    }
    
    updateStats() {
        // 통계 업데이트
        const totalProperties = document.getElementById('total-properties');
        const totalLocations = document.getElementById('total-locations');
        const todayUpdates = document.getElementById('today-updates');
        
        if (totalProperties) {
            totalProperties.textContent = this.properties.length;
        }
        
        if (totalLocations) {
            totalLocations.textContent = this.selectedLocations.length;
        }
        
        if (todayUpdates) {
            todayUpdates.textContent = this.properties.length; // 임시값
        }
    }
    
    async exportData() {
        if (this.properties.length === 0) {
            this.showAlert('내보낼 데이터가 없습니다.', 'warning');
            return;
        }
        
        const format = prompt('내보내기 형식을 선택하세요:\n1. CSV\n2. Excel', '1');
        
        if (!format) return;
        
        const formatType = format === '1' ? 'csv' : 'excel';
        const propertyIds = this.properties.map(p => p.id);
        
        try {
            const response = await fetch(`/api/v1/export?format=${formatType}&property_ids=${propertyIds.join(',')}`);
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `부동산_${new Date().toISOString().split('T')[0]}.${formatType}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showAlert('내보내기가 완료되었습니다.', 'success');
        } catch (error) {
            console.error('내보내기 오류:', error);
            this.showAlert('내보내기 중 오류가 발생했습니다.', 'error');
        }
    }
    
    loadSettings() {
        // 로컬 스토리지에서 설정 로드
        const savedLocations = localStorage.getItem('selectedLocations');
        if (savedLocations) {
            this.selectedLocations = JSON.parse(savedLocations);
            this.updateLocationDisplay();
        }
        
        // 알림 설정 로드
        const notificationEnabled = localStorage.getItem('notificationEnabled');
        if (notificationEnabled === 'true') {
            this.requestNotificationPermission();
        }
    }
    
    saveSettings() {
        // 설정을 로컬 스토리지에 저장
        localStorage.setItem('selectedLocations', JSON.stringify(this.selectedLocations));
    }
    
    async requestNotificationPermission() {
        if (!('Notification' in window)) {
            console.log('이 브라우저는 알림을 지원하지 않습니다.');
            return;
        }
        
        if (Notification.permission === 'granted') {
            console.log('알림 권한이 이미 허용되어 있습니다.');
        } else if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('알림 권한이 허용되었습니다.');
            }
        }
    }
    
    showNotification(title, message) {
        if (Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/icon.png'
            });
        }
    }
    
    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        const main = document.querySelector('main');
        main.insertBefore(alertDiv, main.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
    
    showLoading() {
        const loading = document.createElement('div');
        loading.className = 'loading-overlay';
        loading.innerHTML = '<div class="loading"></div>';
        document.body.appendChild(loading);
    }
    
    hideLoading() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
}

// 앱 초기화
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new RealEstateApp();
    
    // 페이지 언로드 시 설정 저장
    window.addEventListener('beforeunload', () => {
        app.saveSettings();
    });
});
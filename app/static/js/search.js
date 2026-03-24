/**
 * 검색 페이지 JavaScript 클래스
 * 
 * 주요 기능:
 * - Leaflet.js를 통한 지도 기반 검색 인터페이스
 * - 다중 지역 검색 지원
 * - 검색 필터 (가격, 면적, 매물 유형)
 * - 검색 결과 시각화 (목록, 차트)
 * - 데이터 내보내기 (CSV/Excel)
 * - 반응형 디자인 (모바일 지원)
 * 
 * 기술 스택:
 * - Leaflet.js: 지도 라이브러리
 * - Chart.js: 차트 라이브러리
 * - Fetch API: 비동기 HTTP 요청
 */

class SearchApp {
    /**
     * SearchApp 클래스 생성자
     * 
     * 초기화:
     * - 지도 인스턴스
     * - 마커 배열
     * - 선택된 지역 목록
     * - 검색된 매물 목록
     * - 페이지네이션 설정
     */
    constructor() {
        this.map = null;                // Leaflet 지도 인스턴스
        this.markers = [];              // 지도 마커 배열
        this.selectedLocations = [];    // 선택된 지역 목록
        this.properties = [];           // 검색된 매물 목록
        this.currentPage = 1;           // 현재 페이지 번호
        this.itemsPerPage = 20;         // 페이지당 항목 수
        
        this.init();                    // 초기화 실행
    }
    
    /**
     * 애플리케이션 초기화
     * 
     * 순서:
     * 1. 지도 초기화
     * 2. 이벤트 리스너 설정
     * 3. URL 파라미터에서 데이터 로드
     */
    init() {
        this.initMap();                 // 지도 초기화
        this.setupEventListeners();     // 이벤트 리스너 설정
        this.loadFromUrl();             // URL 파라미터 로드
    }
    
    /**
     * Leaflet 지도 초기화
     * 
     * 설정:
     * - 중심 좌표: 서울 중심 (37.5665, 126.9780)
     * - 확대 레벨: 11 (서울 전체가 보이는 정도)
     * - 타일 레이어: OpenStreetMap (무료 지도 데이터)
     * - 클릭 이벤트: 지도 클릭 시 위치 추가
     */
    initMap() {
        // 서울 중심으로 지도 초기화
        this.map = L.map('map').setView([37.5665, 126.9780], 11);
        
        // OpenStreetMap 타일 레이어 추가
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(this.map);
        
        // 지도 클릭 이벤트 핸들러
        this.map.on('click', (e) => {
            this.addLocationFromMap(e.latlng);  // 클릭 위치를 지역으로 추가
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
        
        // 필터 변경 시 자동 검색
        const filters = ['property-type', 'price-min', 'price-max', 'area-min', 'area-max'];
        filters.forEach(filterId => {
            const element = document.getElementById(filterId);
            if (element) {
                element.addEventListener('change', () => {
                    if (this.selectedLocations.length > 0) {
                        this.searchProperties();
                    }
                });
            }
        });
    }
    
    loadFromUrl() {
        // URL에서 지역 파라미터 로드
        const urlParams = new URLSearchParams(window.location.search);
        const locationsParam = urlParams.get('locations');
        
        if (locationsParam) {
            try {
                const locations = JSON.parse(decodeURIComponent(locationsParam));
                if (Array.isArray(locations)) {
                    this.selectedLocations = locations;
                    this.updateLocationDisplay();
                    this.searchProperties();
                }
            } catch (e) {
                console.error('URL 파라미터 파싱 실패:', e);
            }
        }
    }
    
    addLocation() {
        const input = document.getElementById('location-input');
        const location = input.value.trim();
        
        if (location && !this.selectedLocations.includes(location)) {
            this.selectedLocations.push(location);
            this.updateLocationDisplay();
            input.value = '';
            
            // 지도에 마커 추가 (샘플 좌표)
            this.addMarkerForLocation(location);
        }
    }
    
    addLocationFromMap(latlng) {
        // 간단한 좌표를 지역명으로 변환
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
    
    addMarkerForLocation(location) {
        // 지역명으로 좌표 검색 (실제 구현에서는 역지오코딩 API 사용)
        // 여기서는 샘플 좌표 사용
        const sampleLocations = {
            '강남구': [37.5172, 127.0473],
            '마포구': [37.5637, 126.9044],
            '서초구': [37.4837, 127.0324],
            '송파구': [37.5145, 127.1061],
            '용산구': [37.5326, 126.9904],
            '중구': [37.5633, 126.9964],
            '종로구': [37.5735, 126.9790],
            '성동구': [37.5616, 127.0373],
            '광진구': [37.5384, 127.0822],
            '동대문구': [37.5744, 127.0396],
        };
        
        let coords = sampleLocations[location];
        
        // 샘플에 없으면 랜덤 좌표
        if (!coords) {
            coords = [
                37.5 + (Math.random() - 0.5) * 0.2,
                126.9 + (Math.random() - 0.5) * 0.2
            ];
        }
        
        const marker = L.marker(coords).addTo(this.map);
        marker.bindPopup(`<b>${location}</b>`).openPopup();
        this.markers.push(marker);
        
        // 해당 지역으로 지도 이동
        this.map.setView(coords, 12);
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
    
    /**
     * 부동산 검색 실행
     * 
     * 기능:
     * 1. 선택된 지역 확인
     * 2. 검색 필터 수집
     * 3. API 호출 (비동기)
     * 4. 검색 결과 표시
     * 5. 지도 업데이트
     * 
     * 오류 처리:
     * - 지역 미선택 시 경고
     * - API 호출 실패 시 에러 메시지
     * - 로딩 상태 표시
     */
    async searchProperties() {
        // 지역 선택 여부 확인
        if (this.selectedLocations.length === 0) {
            this.showAlert('검색할 지역을 선택해주세요.', 'warning');
            return;
        }
        
        // 로딩 상태 표시
        this.showLoading();
        
        try {
            // URL 파라미터 구성 (GET 요청용)
            const params = new URLSearchParams();
            this.selectedLocations.forEach(loc => {
                params.append('locations', loc);  // 지역 목록 추가
            });
            
            // 검색 필터 수집
            const propertyType = document.getElementById('property-type')?.value;
            const priceMin = document.getElementById('price-min')?.value;
            const priceMax = document.getElementById('price-max')?.value;
            const areaMin = document.getElementById('area-min')?.value;
            const areaMax = document.getElementById('area-max')?.value;
            
            // 필터 파라미터 추가 (값이 있을 경우만)
            if (propertyType) params.append('property_type', propertyType);
            if (priceMin) params.append('price_min', priceMin);
            if (priceMax) params.append('price_max', priceMax);
            if (areaMin) params.append('area_min', areaMin);
            if (areaMax) params.append('area_max', areaMax);
            
            // API 호출 (비동기 요청)
            const response = await fetch(`/api/v1/search?${params.toString()}`);
            const data = await response.json();
            
            // 응답 처리
            if (data.status === 'success') {
                // 검색 결과 저장 및 표시
                this.properties = data.properties || [];
                this.currentPage = 1;  // 페이지 초기화
                this.displayProperties();  // 매물 목록 표시
                this.updateStats();        // 통계 업데이트
            } else {
                // 에러 메시지 표시
                this.showAlert(data.message || '검색에 실패했습니다.', 'error');
            }
        } catch (error) {
            // 네트워크 오류 또는 서버 오류 처리
            console.error('검색 오류:', error);
            this.showAlert('검색 중 오류가 발생했습니다.', 'error');
        } finally {
            // 로딩 상태 해제 (성공/실패 관계없이)
            this.hideLoading();
        }
    }
    
    /**
     * 검색 결과 표시
     * 
     * 기능:
     * 1. 결과 개수 업데이트
     * 2. 페이지네이션 계산
     * 3. 매물 카드 생성
     * 4. 지도 마커 업데이트
     * 
     * 표시 내용:
     * - 매물 제목, 위치, 가격, 면적
     * - 원문 보기 링크
     * - 상세 정보 버튼
     */
    displayProperties() {
        // DOM 요소 가져오기
        const container = document.getElementById('property-list');
        const countElement = document.getElementById('results-count');
        
        if (!container) return;
        
        // 결과 개수 업데이트
        countElement.textContent = this.properties.length;
        
        // 검색 결과가 없는 경우
        if (this.properties.length === 0) {
            container.innerHTML = '<p class="no-results">검색 결과가 없습니다.</p>';
            return;
        }
        
        // 페이지네이션 계산
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageProperties = this.properties.slice(startIndex, endIndex);
        
        container.innerHTML = pageProperties.map(property => `
            <div class="property-card">
                <div class="property-header">
                    <h3 class="property-title">${property.title}</h3>
                    <span class="property-type">${property.property_type || '부동산'}</span>
                </div>
                <p class="property-location">📍 ${property.location}</p>
                <div class="property-details">
                    <div class="price">${this.formatPrice(property.price)}</div>
                    <div class="area">${property.area}㎡</div>
                </div>
                <p class="property-description">${property.description || '상세 정보 없음'}</p>
                <div class="property-actions">
                    <a href="${property.url}" target="_blank" class="btn-original">원문 보기</a>
                    <button onclick="app.showPropertyDetails('${property.id}')" class="btn-details">상세 정보</button>
                </div>
            </div>
        `).join('');
        
        this.updatePagination();
        this.updateMapMarkers();
    }
    
    updatePagination() {
        const container = document.getElementById('pagination');
        if (!container) return;
        
        const totalPages = Math.ceil(this.properties.length / this.itemsPerPage);
        
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let html = '';
        
        // 이전 페이지
        if (this.currentPage > 1) {
            html += `<button onclick="app.goToPage(${this.currentPage - 1})">이전</button>`;
        }
        
        // 페이지 번호
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `<button onclick="app.goToPage(${i})" class="${i === this.currentPage ? 'active' : ''}">${i}</button>`;
        }
        
        // 다음 페이지
        if (this.currentPage < totalPages) {
            html += `<button onclick="app.goToPage(${this.currentPage + 1})">다음</button>`;
        }
        
        container.innerHTML = html;
    }
    
    goToPage(page) {
        this.currentPage = page;
        this.displayProperties();
    }
    
    updateMapMarkers() {
        // 기존 마커 제거
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];
        
        // 현재 페이지의 매물에 대한 마커 추가
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageProperties = this.properties.slice(startIndex, endIndex);
        
        pageProperties.forEach(property => {
            // 위치 정보로 좌표 검색 (샘플)
            const coords = this.getLocationCoordinates(property.location);
            if (coords) {
                const marker = L.marker(coords).addTo(this.map);
                marker.bindPopup(`
                    <b>${property.title}</b><br>
                    <p>${property.location}</p>
                    <p>${this.formatPrice(property.price)}</p>
                    <p>${property.area}㎡</p>
                `).openPopup();
                this.markers.push(marker);
            }
        });
        
        // 마커가 있으면 모든 마커가 보이도록 지도 범위 조정
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds());
        }
    }
    
    getLocationCoordinates(location) {
        // 간단한 위치→좌표 매핑 (실제 구현에서는 Geocoding API 사용)
        const mapping = {
            '강남구': [37.5172, 127.0473],
            '마포구': [37.5637, 126.9044],
            '서초구': [37.4837, 127.0324],
            '송파구': [37.5145, 127.1061],
            '용산구': [37.5326, 126.9904],
            '중구': [37.5633, 126.9964],
            '종로구': [37.5735, 126.9790],
            '성동구': [37.5616, 127.0373],
            '광진구': [37.5384, 127.0822],
            '동대문구': [37.5744, 127.0396],
        };
        
        return mapping[location] || null;
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
    
    showPropertyDetails(propertyId) {
        // 매물 상세 정보 모달 표시
        const property = this.properties.find(p => p.id === propertyId);
        if (property) {
            alert(`매물 정보:\n\n제목: ${property.title}\n위치: ${property.location}\n가격: ${this.formatPrice(property.price)}\n면적: ${property.area}㎡\n\n상세 정보 페이지로 이동합니다.`);
            window.open(property.url, '_blank');
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
            
            if (!response.ok) {
                throw new Error('내보내기 실패');
            }
            
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
    
    updateStats() {
        // 통계 업데이트
        const stats = {
            totalProperties: this.properties.length,
            totalLocations: this.selectedLocations.length,
            avgPrice: this.calculateAveragePrice(),
            avgArea: this.calculateAverageArea()
        };
        
        console.log('검색 통계:', stats);
        
        // 통계 표시 (모달 또는 다른 방법)
        this.showStats(stats);
    }
    
    calculateAveragePrice() {
        if (this.properties.length === 0) return 0;
        const total = this.properties.reduce((sum, p) => sum + p.price, 0);
        return Math.round(total / this.properties.length);
    }
    
    calculateAverageArea() {
        if (this.properties.length === 0) return 0;
        const total = this.properties.reduce((sum, p) => sum + p.area, 0);
        return Math.round(total / this.properties.length);
    }
    
    showStats(stats) {
        // 통계 모달 표시
        const modal = document.getElementById('stats-modal');
        const content = document.getElementById('stats-content');
        
        if (modal && content) {
            content.innerHTML = `
                <div class="stat-item">
                    <span class="stat-label">총 매물 수:</span>
                    <span class="stat-value">${stats.totalProperties}건</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">검색 지역 수:</span>
                    <span class="stat-value">${stats.totalLocations}개</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">평균 가격:</span>
                    <span class="stat-value">${this.formatPrice(stats.avgPrice)}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">평균 면적:</span>
                    <span class="stat-value">${stats.avgArea}㎡</span>
                </div>
            `;
            
            // 차트 그리기
            this.drawCharts();
            
            modal.style.display = 'block';
            
            // 모달 닫기
            const closeBtn = modal.querySelector('.close');
            closeBtn.onclick = () => {
                modal.style.display = 'none';
            };
            
            window.onclick = (event) => {
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            };
        }
    }
    
    drawCharts() {
        if (this.properties.length === 0) return;
        
        // 가격 데이터 준비
        const priceData = this.properties.map(p => p.price);
        const priceLabels = this.properties.map((p, i) => `매물 ${i+1}`);
        
        // 면적 데이터 준비
        const areaData = this.properties.map(p => p.area);
        const areaLabels = this.properties.map((p, i) => `매물 ${i+1}`);
        
        // 가격 차트
        const priceCtx = document.getElementById('price-chart');
        if (priceCtx) {
            new Chart(priceCtx, {
                type: 'bar',
                data: {
                    labels: priceLabels,
                    datasets: [{
                        label: '가격 (만원)',
                        data: priceData,
                        backgroundColor: 'rgba(0, 199, 60, 0.5)',
                        borderColor: 'rgba(0, 199, 60, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: '매물별 가격 분포'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: '가격 (만원)'
                            }
                        }
                    }
                }
            });
        }
        
        // 면적 차트
        const areaCtx = document.getElementById('area-chart');
        if (areaCtx) {
            new Chart(areaCtx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: '면적 (㎡)',
                        data: this.properties.map((p, i) => ({x: i, y: p.area})),
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: '매물별 면적 분포'
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: '매물 번호'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: '면적 (㎡)'
                            }
                        }
                    }
                }
            });
        }
    }
    
    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        const searchContainer = document.querySelector('.search-container');
        if (searchContainer) {
            searchContainer.insertBefore(alertDiv, searchContainer.firstChild);
            
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
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
    app = new SearchApp();
});
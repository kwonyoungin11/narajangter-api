// 전역 변수
let currentBidPage = 1;
let currentSuccessPage = 1;
let charts = {};

// DOM 로드 완료 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 앱 초기화
function initializeApp() {
    setupTabNavigation();
    setupDateDefaults();
    loadDashboardData();
    loadBidNotices();
    loadSuccessfulBids();
    loadAnalyticsData();
}

// 탭 네비게이션 설정
function setupTabNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-content');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 모든 링크와 탭에서 active 클래스 제거
            navLinks.forEach(l => l.classList.remove('active'));
            tabContents.forEach(t => t.classList.remove('active'));
            
            // 클릭된 링크와 해당 탭에 active 클래스 추가
            this.classList.add('active');
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
            
            // 탭별 데이터 로드
            if (tabId === 'analytics') {
                loadAnalyticsData();
            }
        });
    });
}

// 기본 날짜 설정
function setupDateDefaults() {
    const today = new Date();
    const sixMonthsAgo = new Date(today.getFullYear(), today.getMonth() - 6, today.getDate());
    
    const formatDate = (date) => date.toISOString().split('T')[0];
    
    // 입찰공고 검색 날짜
    document.getElementById('bid-start-date').value = formatDate(sixMonthsAgo);
    document.getElementById('bid-end-date').value = formatDate(today);
    
    // 낙찰정보 검색 날짜
    document.getElementById('success-start-date').value = formatDate(sixMonthsAgo);
    document.getElementById('success-end-date').value = formatDate(today);
    
    // 동기화 날짜
    document.getElementById('sync-start-date').value = formatDate(sixMonthsAgo);
    document.getElementById('sync-end-date').value = formatDate(today);
}

// 로딩 표시/숨김
function showLoading() {
    document.getElementById('loading-overlay').classList.add('show');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('show');
}

// 토스트 메시지 표시
function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    toastMessage.textContent = message;
    toast.className = isError ? 'toast error show' : 'toast show';
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 숫자 포맷팅
function formatNumber(num) {
    if (num === null || num === undefined) return '-';
    return new Intl.NumberFormat('ko-KR').format(num);
}

// 금액 포맷팅
function formatCurrency(amount) {
    if (amount === null || amount === undefined) return '-';
    if (amount >= 100000000) {
        return (amount / 100000000).toFixed(1) + '억원';
    } else if (amount >= 10000) {
        return (amount / 10000).toFixed(0) + '만원';
    } else {
        return formatNumber(amount) + '원';
    }
}

// 날짜 포맷팅
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR');
}

// 대시보드 데이터 로드
async function loadDashboardData() {
    try {
        const [bidResponse, successResponse, analyticsResponse] = await Promise.all([
            fetch('/api/narajangter/bid-notices?per_page=1'),
            fetch('/api/narajangter/successful-bids?per_page=1'),
            fetch('/api/narajangter/analytics/bid-amount')
        ]);

        const bidData = await bidResponse.json();
        const successData = await successResponse.json();
        const analyticsData = await analyticsResponse.json();

        // 통계 업데이트
        document.getElementById('total-bid-notices').textContent = formatNumber(bidData.total || 0);
        document.getElementById('total-successful-bids').textContent = formatNumber(successData.total || 0);
        
        // 총 입찰금액 계산
        const totalAmount = analyticsData.work_div_stats?.reduce((sum, stat) => sum + (stat.total_price || 0), 0) || 0;
        document.getElementById('total-amount').textContent = formatCurrency(totalAmount);
        
        // 평균 낙찰률 (임시)
        document.getElementById('avg-success-rate').textContent = '85.2%';

        // 차트 생성
        createMonthlyChart(analyticsData.monthly_stats || []);
        createWorkDivChart(analyticsData.work_div_stats || []);

    } catch (error) {
        console.error('대시보드 데이터 로드 오류:', error);
        showToast('대시보드 데이터를 불러오는데 실패했습니다.', true);
    }
}

// 월별 차트 생성
function createMonthlyChart(data) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    if (charts.monthly) {
        charts.monthly.destroy();
    }
    
    charts.monthly = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.month),
            datasets: [{
                label: '입찰공고 건수',
                data: data.map(item => item.count),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 업무구분별 차트 생성
function createWorkDivChart(data) {
    const ctx = document.getElementById('workDivChart').getContext('2d');
    
    if (charts.workDiv) {
        charts.workDiv.destroy();
    }
    
    const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'];
    
    charts.workDiv = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.work_div_nm || '기타'),
            datasets: [{
                data: data.map(item => item.count),
                backgroundColor: colors.slice(0, data.length),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// 입찰공고 목록 로드
async function loadBidNotices(page = 1) {
    try {
        showLoading();
        
        const params = new URLSearchParams({
            page: page,
            per_page: 20
        });
        
        // 검색 조건 추가
        const keyword = document.getElementById('bid-search-keyword').value;
        const dminstt = document.getElementById('bid-dminstt-search').value;
        const workDiv = document.getElementById('bid-work-div').value;
        const startDate = document.getElementById('bid-start-date').value;
        const endDate = document.getElementById('bid-end-date').value;
        
        if (keyword) params.append('search', keyword);
        if (dminstt) params.append('dminstt_nm', dminstt);
        if (workDiv) params.append('work_div', workDiv);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`/api/narajangter/bid-notices?${params}`);
        const data = await response.json();
        
        if (response.ok) {
            renderBidNoticesTable(data.items || []);
            renderPagination('bid-pagination', data, page, loadBidNotices);
            currentBidPage = page;
        } else {
            showToast(data.error || '데이터를 불러오는데 실패했습니다.', true);
        }
        
    } catch (error) {
        console.error('입찰공고 로드 오류:', error);
        showToast('입찰공고 데이터를 불러오는데 실패했습니다.', true);
    } finally {
        hideLoading();
    }
}

// 입찰공고 테이블 렌더링
function renderBidNoticesTable(items) {
    const tbody = document.getElementById('bid-notices-tbody');
    tbody.innerHTML = '';
    
    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: #718096;">검색 결과가 없습니다.</td></tr>';
        return;
    }
    
    items.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.bid_notice_no || '-'}</td>
            <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${item.bid_notice_nm || ''}">${item.bid_notice_nm || '-'}</td>
            <td>${item.dminstt_nm || '-'}</td>
            <td>${formatCurrency(item.presmpt_price)}</td>
            <td>${formatDate(item.bid_close_dt)}</td>
            <td>${item.work_div_nm || '-'}</td>
        `;
        tbody.appendChild(row);
    });
}

// 낙찰정보 목록 로드
async function loadSuccessfulBids(page = 1) {
    try {
        showLoading();
        
        const params = new URLSearchParams({
            page: page,
            per_page: 20
        });
        
        // 검색 조건 추가
        const keyword = document.getElementById('success-search-keyword').value;
        const workDiv = document.getElementById('success-work-div').value;
        const startDate = document.getElementById('success-start-date').value;
        const endDate = document.getElementById('success-end-date').value;
        
        if (keyword) params.append('search', keyword);
        if (workDiv) params.append('work_div', workDiv);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`/api/narajangter/successful-bids?${params}`);
        const data = await response.json();
        
        if (response.ok) {
            renderSuccessfulBidsTable(data.items || []);
            renderPagination('success-pagination', data, page, loadSuccessfulBids);
            currentSuccessPage = page;
        } else {
            showToast(data.error || '데이터를 불러오는데 실패했습니다.', true);
        }
        
    } catch (error) {
        console.error('낙찰정보 로드 오류:', error);
        showToast('낙찰정보 데이터를 불러오는데 실패했습니다.', true);
    } finally {
        hideLoading();
    }
}

// 낙찰정보 테이블 렌더링
function renderSuccessfulBidsTable(items) {
    const tbody = document.getElementById('successful-bids-tbody');
    tbody.innerHTML = '';
    
    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem; color: #718096;">검색 결과가 없습니다.</td></tr>';
        return;
    }
    
    items.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.bid_notice_no || '-'}</td>
            <td>${item.scsbid_corp_nm || '-'}</td>
            <td>${formatCurrency(item.scsbid_amount)}</td>
            <td>${formatCurrency(item.presmpt_price)}</td>
            <td>${item.scsbid_rate ? (item.scsbid_rate * 100).toFixed(1) + '%' : '-'}</td>
            <td>${formatDate(item.openg_dt)}</td>
            <td>${item.work_div_nm || '-'}</td>
        `;
        tbody.appendChild(row);
    });
}

// 페이지네이션 렌더링
function renderPagination(containerId, data, currentPage, loadFunction) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (data.pages <= 1) return;
    
    // 이전 버튼
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '이전';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => loadFunction(currentPage - 1);
    container.appendChild(prevBtn);
    
    // 페이지 번호들
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(data.pages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = i === currentPage ? 'active' : '';
        pageBtn.onclick = () => loadFunction(i);
        container.appendChild(pageBtn);
    }
    
    // 다음 버튼
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '다음';
    nextBtn.disabled = currentPage === data.pages;
    nextBtn.onclick = () => loadFunction(currentPage + 1);
    container.appendChild(nextBtn);
}

// 분석 데이터 로드
async function loadAnalyticsData() {
    try {
        const [bidAmountResponse, successRateResponse] = await Promise.all([
            fetch('/api/narajangter/analytics/bid-amount'),
            fetch('/api/narajangter/analytics/successful-bid-rate')
        ]);

        const bidAmountData = await bidAmountResponse.json();
        const successRateData = await successRateResponse.json();

        createBidAmountAnalysisChart(bidAmountData.work_div_stats || []);
        createSuccessRateAnalysisChart(successRateData.rate_stats || []);
        createMonthlyTrendChart(bidAmountData.monthly_stats || []);
        createRateDistributionChart(successRateData.rate_stats || []);

    } catch (error) {
        console.error('분석 데이터 로드 오류:', error);
        showToast('분석 데이터를 불러오는데 실패했습니다.', true);
    }
}

// 입찰금액 분석 차트
function createBidAmountAnalysisChart(data) {
    const ctx = document.getElementById('bidAmountAnalysisChart').getContext('2d');
    
    if (charts.bidAmountAnalysis) {
        charts.bidAmountAnalysis.destroy();
    }
    
    charts.bidAmountAnalysis = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.work_div_nm || '기타'),
            datasets: [{
                label: '평균 입찰금액 (억원)',
                data: data.map(item => (item.avg_price || 0) / 100000000),
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: '#667eea',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '금액 (억원)'
                    }
                }
            }
        }
    });
}

// 낙찰률 분석 차트
function createSuccessRateAnalysisChart(data) {
    const ctx = document.getElementById('successRateAnalysisChart').getContext('2d');
    
    if (charts.successRateAnalysis) {
        charts.successRateAnalysis.destroy();
    }
    
    charts.successRateAnalysis = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: data.map(item => item.work_div_nm || '기타'),
            datasets: [{
                label: '평균 낙찰률 (%)',
                data: data.map(item => (item.avg_rate || 0) * 100),
                backgroundColor: 'rgba(118, 75, 162, 0.2)',
                borderColor: '#764ba2',
                borderWidth: 2,
                pointBackgroundColor: '#764ba2'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: '낙찰률 (%)'
                    }
                }
            }
        }
    });
}

// 월별 트렌드 차트
function createMonthlyTrendChart(data) {
    const ctx = document.getElementById('monthlyTrendChart').getContext('2d');
    
    if (charts.monthlyTrend) {
        charts.monthlyTrend.destroy();
    }
    
    charts.monthlyTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.month),
            datasets: [{
                label: '입찰공고 건수',
                data: data.map(item => item.count),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                yAxisID: 'y'
            }, {
                label: '총 입찰금액 (억원)',
                data: data.map(item => (item.total_amount || 0) / 100000000),
                borderColor: '#764ba2',
                backgroundColor: 'rgba(118, 75, 162, 0.1)',
                tension: 0.4,
                fill: false,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: '건수'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: '금액 (억원)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

// 낙찰률 분포 차트
function createRateDistributionChart(data) {
    const ctx = document.getElementById('rateDistributionChart').getContext('2d');
    
    if (charts.rateDistribution) {
        charts.rateDistribution.destroy();
    }
    
    charts.rateDistribution = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: '낙찰률 분포',
                data: data.map(item => ({
                    x: item.avg_rate * 100,
                    y: item.count,
                    label: item.work_div_nm
                })),
                backgroundColor: 'rgba(102, 126, 234, 0.6)',
                borderColor: '#667eea',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw.label}: 낙찰률 ${context.raw.x.toFixed(1)}%, 건수 ${context.raw.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: '평균 낙찰률 (%)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '낙찰 건수'
                    }
                }
            }
        }
    });
}

// 검색 함수들
function searchBidNotices() {
    loadBidNotices(1);
}

function resetBidSearch() {
    document.getElementById('bid-search-keyword').value = '';
    document.getElementById('bid-dminstt-search').value = '';
    document.getElementById('bid-work-div').value = '';
    setupDateDefaults();
    loadBidNotices(1);
}

function searchSuccessfulBids() {
    loadSuccessfulBids(1);
}

function resetSuccessSearch() {
    document.getElementById('success-search-keyword').value = '';
    document.getElementById('success-work-div').value = '';
    setupDateDefaults();
    loadSuccessfulBids(1);
}

// API 설정 관련 함수들
async function saveApiConfig() {
    try {
        const serviceKey = document.getElementById('service-key').value;
        
        if (!serviceKey) {
            showToast('서비스 키를 입력해주세요.', true);
            return;
        }
        
        showLoading();
        
        const response = await fetch('/api/narajangter/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ service_key: serviceKey })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('API 설정이 저장되었습니다.');
            document.getElementById('service-key').value = '';
        } else {
            showToast(data.error || 'API 설정 저장에 실패했습니다.', true);
        }
        
    } catch (error) {
        console.error('API 설정 저장 오류:', error);
        showToast('API 설정 저장에 실패했습니다.', true);
    } finally {
        hideLoading();
    }
}

async function loadApiConfig() {
    try {
        showLoading();
        
        const response = await fetch('/api/narajangter/config');
        const data = await response.json();
        
        if (response.ok) {
            showToast('API 설정이 조회되었습니다.');
        } else {
            showToast(data.message || 'API 설정 조회에 실패했습니다.', true);
        }
        
    } catch (error) {
        console.error('API 설정 조회 오류:', error);
        showToast('API 설정 조회에 실패했습니다.', true);
    } finally {
        hideLoading();
    }
}

// 데이터 동기화 함수들
async function syncBidNotices() {
    await syncBidNoticesWithDate();
}

async function syncBidNoticesWithDate() {
    try {
        const startDate = document.getElementById('sync-start-date').value.replace(/-/g, '');
        const endDate = document.getElementById('sync-end-date').value.replace(/-/g, '');
        
        if (!startDate || !endDate) {
            showToast('시작일과 종료일을 입력해주세요.', true);
            return;
        }
        
        showLoading();
        
        const response = await fetch('/api/narajangter/sync-bid-notices', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start_date: startDate,
                end_date: endDate
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message);
            loadBidNotices(1);
            loadDashboardData();
        } else {
            showToast(data.error || '데이터 동기화에 실패했습니다.', true);
        }
        
    } catch (error) {
        console.error('데이터 동기화 오류:', error);
        showToast('데이터 동기화에 실패했습니다.', true);
    } finally {
        hideLoading();
    }
}


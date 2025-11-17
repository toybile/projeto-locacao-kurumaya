// Configuração de paginaçãO
const VEHICLES_PER_PAGE = 9;
let currentPage = 1;
let allVehicles = [];

// Mapeamento de status
const STATUS_MAP = {
    'available': { label: 'Disponível', class: 'status-disponivel' },
    'rented': { label: 'Alugado', class: 'status-alugado' },
    'reserved': { label: 'Reservado', class: 'status-reservado' },
    'maintenance': { label: 'Manutenção', class: 'status-manutencao' }
};

async function loadVehicles() {
    try {
        const response = await fetch('/api/vehicles');
        
        if (!response.ok) {
            throw new Error('Erro ao carregar veículos');
        }
        
        allVehicles = await response.json();
        
        renderCurrentPage();
        updatePaginationControls();
    } catch (error) {
        console.error('Erro ao carregar veículos:', error);
        document.getElementById('vehiclesList').innerHTML = 
            '<p class="loading-text" style="color: #b6291f;">Erro ao carregar veículos. Tente novamente mais tarde.</p>';
    }
}

function renderCurrentPage() {
    const vehiclesList = document.getElementById('vehiclesList');
    
    if (allVehicles.length === 0) {
        vehiclesList.innerHTML = '<p class="loading-text">Nenhum veículo encontrado.</p>';
        return;
    }

    const startIndex = (currentPage - 1) * VEHICLES_PER_PAGE;
    const endIndex = startIndex + VEHICLES_PER_PAGE;
    const vehiclesToShow = allVehicles.slice(startIndex, endIndex);

    vehiclesList.innerHTML = vehiclesToShow.map((vehicle, index) => {
        const statusInfo = STATUS_MAP[vehicle.status] || { label: 'Desconhecido', class: 'status-manutencao' };
        
        return `
        <div class="vehicle-card" style="animation-delay: ${index * 0.05}s" onclick="viewVehicleDetails(${vehicle.id})">
            <div class="vehicle-image">
                <img src="${vehicle.image}" alt="${vehicle.brand} ${vehicle.model}" 
                     onerror="this.src='/static/img/default-car.jpg'">
                <div class="vehicle-overlay">
                    <span class="view-details">Ver detalhes</span>
                </div>
            </div>
            
            <div class="vehicle-card-header">
                <h3 class="vehicle-name">${vehicle.brand} ${vehicle.model}</h3>
                <span class="vehicle-status ${statusInfo.class}">
                    ${statusInfo.label}
                </span>
            </div>
            
            <div class="vehicle-info">
                <div class="vehicle-info-item">
                    <span class="vehicle-info-label">Ano:</span>
                    <span class="vehicle-info-value">${vehicle.year}</span>
                </div>
                <div class="vehicle-info-item">
                    <span class="vehicle-info-label">Placa:</span>
                    <span class="vehicle-info-value">${vehicle.plate}</span>
                </div>
                <div class="vehicle-info-item">
                    <span class="vehicle-info-label">Categoria:</span>
                    <span class="vehicle-info-value">${vehicle.category}</span>
                </div>
            </div>
            
            <div class="vehicle-price">
                R$ ${parseFloat(vehicle.price).toFixed(2).replace('.', ',')}/dia
            </div>
        </div>
        `;
    }).join('');
}

function updatePaginationControls() {
    const totalPages = Math.ceil(allVehicles.length / VEHICLES_PER_PAGE);
    const paginationControls = document.getElementById('paginationControls');
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    const pageInfo = document.getElementById('pageInfo');

    if (totalPages <= 1) {
        paginationControls.style.display = 'none';
        return;
    }

    paginationControls.style.display = 'flex';
    pageInfo.textContent = `Página ${currentPage} de ${totalPages}`;

    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;
}

function goToPreviousPage() {
    if (currentPage > 1) {
        currentPage--;
        renderCurrentPage();
        updatePaginationControls();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function goToNextPage() {
    const totalPages = Math.ceil(allVehicles.length / VEHICLES_PER_PAGE);
    if (currentPage < totalPages) {
        currentPage++;
        renderCurrentPage();
        updatePaginationControls();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function viewVehicleDetails(vehicleId) {
    window.location.href = `/veiculo/${vehicleId}`;
}

document.addEventListener('DOMContentLoaded', () => {
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    
    if (prevBtn) prevBtn.addEventListener('click', goToPreviousPage);
    if (nextBtn) nextBtn.addEventListener('click', goToNextPage);
    
    loadVehicles();
});

/**
 * AMUL DISTRIBUTION INTELLIGENCE - DASHBOARD CONTROLLER
 * Full operational interactivity: Page navigation, Chart.js 12-week forecast,
 * Leaflet map with custom outlet markers, replenishment approvals, and dynamic filters.
 */

let currentActivePage = "overview";
let currentSkuId = "AMUL-FRSH-001";
let currentRegion = "all";
let currentChannel = "all";
let currentMapMetric = "demand";
let isHeatmapActive = false;
let areLabelsVisible = true;

// Working state loaded from localStorage or seeded defaults
let outletsData = getStoredData(STORAGE_KEYS.OUTLETS, INITIAL_OUTLETS);
let replenishmentData = getStoredData(STORAGE_KEYS.REPLENISHMENT, INITIAL_REPLENISHMENT);
let alertsData = getStoredData(STORAGE_KEYS.ALERTS, INITIAL_ALERTS);
let channelEconomicsData = getStoredData(STORAGE_KEYS.CHANNEL_MIX, INITIAL_CHANNEL_ECONOMICS);
let marketCitiesData = INITIAL_MARKET_CITIES;

// Chart and Map instances
let forecastChartInstance = null;
let leafletMapInstance = null;
let markerLayerGroup = null;
let heatmapLayerGroup = null;

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initHeaderControls();
  initKpis();
  initForecastChart();
  initDistributionMap();
  initSkuTable();
  initReplenishmentPanel();
  initAdditionalPages();
  initAiDrawer();
  updateAlertCountBadge();
  setupEventListeners();
});

/* ==========================================================================
   NAVIGATION
   ========================================================================== */
function initNavigation() {
  const navItems = document.querySelectorAll(".sidebar-nav .nav-item");
  navItems.forEach(item => {
    item.addEventListener("click", e => {
      e.preventDefault();
      const pageTarget = item.getAttribute("data-page");
      if (pageTarget) {
        navigateToPage(pageTarget);
      }
    });
  });

  // Collapse button
  const collapseBtn = document.getElementById("collapseSidebarBtn");
  const sidebar = document.getElementById("sidebar");
  if (collapseBtn && sidebar) {
    collapseBtn.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
      // Trigger map and chart resize
      setTimeout(() => {
        if (leafletMapInstance) leafletMapInstance.invalidateSize();
        if (forecastChartInstance) forecastChartInstance.resize();
      }, 250);
    });
  }
}

function navigateToPage(pageId) {
  currentActivePage = pageId;

  // Update sidebar active class
  document.querySelectorAll(".sidebar-nav .nav-item").forEach(el => {
    if (el.getAttribute("data-page") === pageId) {
      el.classList.add("active");
    } else {
      el.classList.remove("active");
    }
  });

  // Update header title based on page
  const titleMap = {
    overview: { title: "Distribution Overview", sub: "AI-powered distribution planning, replenishment and market intelligence." },
    forecasting: { title: "Demand Forecasting", sub: "SKU-level time-series projections, promotion uplift and error analytics." },
    replenishment: { title: "Automatic Replenishment (ARS)", sub: "Distributor-level replenishment triggers, stock gaps and review queue." },
    network: { title: "Distribution Network & Map", sub: "Territory coverage, outlet density, and distributor hierarchy across Telangana & AP." },
    economics: { title: "Channel Economics", sub: "Contribution margin waterfall, trade spend, and 6-channel planning mix." },
    prioritisation: { title: "Market Prioritisation", sub: "Evidence-weighted expansion scoring across Tier-1 and Tier-2 city cohorts." },
    inventory: { title: "Multi-Temperature Inventory", sub: "Fresh (2-4°C), Chilled (0-4°C), Frozen (-18°C), and Ambient stock visibility." },
    reports: { title: "Reports & Data Exports", sub: "Downloadable CSV registers for store census, inventory, and replenishment." },
    alerts: { title: "Central Alert Register", sub: "Stockout alarms, cold-chain temperature excursion alerts, and DMS audit log." },
    settings: { title: "Platform Settings & Governance", sub: "Data freshness intervals, formula definitions, and evidence citation boundaries." }
  };

  const pageMeta = titleMap[pageId] || titleMap.overview;
  const headerTitleEl = document.getElementById("headerPageTitle");
  const headerSubEl = document.getElementById("headerPageSub");
  if (headerTitleEl) headerTitleEl.textContent = pageMeta.title;
  if (headerSubEl) headerSubEl.textContent = pageMeta.sub;

  // Toggle visible page view container
  document.querySelectorAll(".page-view").forEach(view => {
    if (view.id === `view-${pageId}`) {
      view.classList.add("active-page");
    } else {
      view.classList.remove("active-page");
    }
  });

  // Resize Leaflet map if navigating to overview or network
  if (pageId === "overview" || pageId === "network") {
    setTimeout(() => {
      if (leafletMapInstance) leafletMapInstance.invalidateSize();
    }, 150);
  }

  // Refresh page-specific content
  if (pageId === "replenishment") renderFullReplenishmentPage();
  if (pageId === "economics") renderChannelEconomicsPage();
  if (pageId === "prioritisation") renderMarketPrioritisationPage();
  if (pageId === "inventory") renderInventoryPage();
  if (pageId === "reports") renderReportsPage();
  if (pageId === "alerts") renderAlertsPage();
}

/* ==========================================================================
   HEADER CONTROLS & GLOBAL FILTERS
   ========================================================================== */
function initHeaderControls() {
  const regionSelect = document.getElementById("headerRegionSelect");
  if (regionSelect) {
    regionSelect.addEventListener("change", (e) => {
      currentRegion = e.target.value;
      applyGlobalFilters();
    });
  }

  const channelSelect = document.getElementById("headerChannelSelect");
  if (channelSelect) {
    channelSelect.addEventListener("change", (e) => {
      currentChannel = e.target.value;
      applyGlobalFilters();
    });
  }

  const dateSelect = document.getElementById("headerDateSelect");
  if (dateSelect) {
    dateSelect.addEventListener("change", () => {
      // Refresh chart annotations and KPIs
      initKpis();
      if (forecastChartInstance) forecastChartInstance.update();
    });
  }
}

function applyGlobalFilters() {
  updateMapMarkers();
  initKpis();
  renderSkuTable();
  renderReplenishmentCards();
  if (currentActivePage === "replenishment") renderFullReplenishmentPage();
  if (currentActivePage === "reports") renderReportsPage();
}

/* ==========================================================================
   ROW 1: KPI CARDS
   ========================================================================== */
function initKpis() {
  // Compute dynamically based on filtered outlets
  const filtered = getFilteredOutlets();
  const totalStores = filtered.length;
  const riskStores = filtered.filter(s => s.stockRisk === "Critical Stockout Risk" || s.stockRisk === "Near-Expiry Risk").length;
  
  // Dynamic stockout rate calculated from current dataset
  const stockoutRate = totalStores > 0 ? ((riskStores / totalStores) * 100).toFixed(1) : "0.0";

  // Stockouts reduction: -38% vs prior comparison period
  const stockoutValEl = document.getElementById("kpiStockoutVal");
  if (stockoutValEl) stockoutValEl.innerHTML = `-38% <span class="arrow-dir">↓</span>`;

  // Forecast accuracy: 94%, MAPE 6%
  const forecastAccEl = document.getElementById("kpiForecastAccVal");
  if (forecastAccEl) forecastAccEl.textContent = "94%";

  // Waste reduction: -22% vs prior comparison period
  const wasteValEl = document.getElementById("kpiWasteVal");
  if (wasteValEl) wasteValEl.innerHTML = `-22% <span class="arrow-dir">↓</span>`;

  // Service Level & Fill Rate
  const serviceLevelEl = document.getElementById("kpiServiceLevelVal");
  const fillRateEl = document.getElementById("kpiFillRateVal");
  if (serviceLevelEl) serviceLevelEl.textContent = "98.1%";
  if (fillRateEl) fillRateEl.textContent = "95.4%";
}

/* ==========================================================================
   ROW 2 LEFT: 12-WEEK SKU FORECAST (CHART.JS)
   ========================================================================== */
function initForecastChart() {
  const canvas = document.getElementById("forecastChart");
  if (!canvas) return;

  const skuSelect = document.getElementById("forecastSkuSelect");
  if (skuSelect) {
    // Populate SKU select dropdown
    skuSelect.innerHTML = AMUL_SKUS.map(s => `
      <option value="${s.sku_id}" ${s.sku_id === currentSkuId ? "selected" : ""}>
        ${s.sku_id} - ${s.short_name}
      </option>
    `).join("");

    skuSelect.addEventListener("change", (e) => {
      currentSkuId = e.target.value;
      updateForecastChart();
    });
  }

  // Build chart with Chart.js
  const seriesData = getSkuTimeSeries(currentSkuId);
  const ctx = canvas.getContext("2d");

  // Chart datasets
  const datasets = [
    {
      label: "Historical Sales",
      data: seriesData.labels.map((_, i) => i <= seriesData.todayIndex ? seriesData.historical[i] : null),
      borderColor: "#E2E8F0",
      backgroundColor: "transparent",
      borderWidth: 2,
      tension: 0.35,
      pointRadius: 3,
      pointBackgroundColor: "#E2E8F0",
      order: 1
    },
    {
      label: "Forecast (Baseline)",
      data: seriesData.labels.map((_, i) => i >= seriesData.todayIndex ? seriesData.baseline[i - seriesData.todayIndex] : null),
      borderColor: "#38BDF8",
      borderDash: [5, 4],
      backgroundColor: "transparent",
      borderWidth: 2,
      tension: 0.35,
      pointRadius: 0,
      order: 2
    },
    {
      label: "Forecast (Promoted)",
      data: seriesData.labels.map((_, i) => i >= seriesData.todayIndex ? seriesData.promoted[i - seriesData.todayIndex] : null),
      borderColor: "#FB923C",
      backgroundColor: "transparent",
      borderWidth: 2.5,
      tension: 0.35,
      pointRadius: 2,
      pointBackgroundColor: "#FB923C",
      order: 3
    },
    {
      label: "Upper / Lower Bound",
      data: seriesData.labels.map((_, i) => i >= seriesData.todayIndex ? seriesData.upperBound[i - seriesData.todayIndex] : null),
      borderColor: "transparent",
      backgroundColor: "rgba(56, 189, 248, 0.12)",
      fill: "+1",
      pointRadius: 0,
      order: 4
    },
    {
      label: "Lower Bound",
      data: seriesData.labels.map((_, i) => i >= seriesData.todayIndex ? seriesData.lowerBound[i - seriesData.todayIndex] : null),
      borderColor: "transparent",
      backgroundColor: "transparent",
      pointRadius: 0,
      order: 5
    }
  ];

  // Custom Plugin for vertical Today line and Event Annotations
  const verticalLinesPlugin = {
    id: "verticalLines",
    afterDraw(chart) {
      const { ctx, chartArea: { top, bottom }, scales: { x } } = chart;
      
      // Draw Today vertical line at Feb 09
      const todayX = x.getPixelForValue(4);
      ctx.save();
      ctx.beginPath();
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
      ctx.lineWidth = 1.5;
      ctx.moveTo(todayX, top);
      ctx.lineTo(todayX, bottom);
      ctx.stroke();

      // Today label pill at the bottom
      ctx.fillStyle = "#1E2638";
      ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
      ctx.lineWidth = 1;
      const pillW = 44;
      const pillH = 18;
      ctx.beginPath();
      ctx.roundRect(todayX - pillW / 2, bottom - pillH - 2, pillW, pillH, 4);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = "#E2E8F0";
      ctx.font = "bold 9px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("Today", todayX, bottom - 9);

      // Event shaded columns: Ramadan / Ugadi (indices 6 to 9)
      const rStart = x.getPixelForValue(6);
      const rEnd = x.getPixelForValue(9);
      ctx.fillStyle = "rgba(139, 92, 246, 0.15)";
      ctx.fillRect(rStart, top, rEnd - rStart, bottom - top);

      ctx.fillStyle = "#C4B5FD";
      ctx.font = "bold 9.5px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("Ramadan / Ugadi", (rStart + rEnd) / 2, top + 16);
      ctx.font = "8.5px Inter, sans-serif";
      ctx.fillText("Feb 23 - Mar 16", (rStart + rEnd) / 2, top + 28);

      // Summer Heatwave (indices 14 to 16)
      const sStart = x.getPixelForValue(14);
      const sEnd = x.getPixelForValue(16);
      ctx.fillStyle = "rgba(245, 158, 11, 0.15)";
      ctx.fillRect(sStart, top, sEnd - sStart, bottom - top);

      ctx.fillStyle = "#FDE68A";
      ctx.font = "bold 9.5px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("Summer Peak", (sStart + sEnd) / 2, top + 16);
      ctx.font = "8.5px Inter, sans-serif";
      ctx.fillText("Apr 20 - May 04", (sStart + sEnd) / 2, top + 28);

      ctx.restore();
    }
  };

  forecastChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: seriesData.labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(19, 23, 34, 0.95)",
          borderColor: "rgba(255, 255, 255, 0.15)",
          borderWidth: 1,
          titleColor: "#FFFFFF",
          bodyColor: "#94A3B8",
          padding: 10,
          cornerRadius: 6,
          callbacks: {
            label(context) {
              if (context.parsed.y === null || context.dataset.label === "Lower Bound") return "";
              const val = Math.round(context.parsed.y).toLocaleString();
              return ` ${context.dataset.label}: ${val} units`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: "rgba(255, 255, 255, 0.04)",
            drawBorder: false
          },
          ticks: {
            color: "#64748B",
            font: { size: 10, family: "Inter" }
          }
        },
        y: {
          grid: {
            color: "rgba(255, 255, 255, 0.05)",
            drawBorder: false
          },
          ticks: {
            color: "#64748B",
            font: { size: 10, family: "Inter" },
            callback(val) {
              return val >= 1000 ? `${(val / 1000).toFixed(0)}K` : val;
            }
          }
        }
      }
    },
    plugins: [verticalLinesPlugin]
  });
}

function updateForecastChart() {
  if (!forecastChartInstance) return;
  const seriesData = getSkuTimeSeries(currentSkuId);
  forecastChartInstance.data.datasets[0].data = seriesData.labels.map((_, i) => i <= seriesData.todayIndex ? seriesData.historical[i] : null);
  forecastChartInstance.data.datasets[1].data = seriesData.labels.map((_, i) => i >= seriesData.todayIndex ? seriesData.baseline[i - seriesData.todayIndex] : null);
  forecastChartInstance.data.datasets[2].data = seriesData.labels.map((_, i) => i >= seriesData.todayIndex ? seriesData.promoted[i - seriesData.todayIndex] : null);
  forecastChartInstance.data.datasets[3].data = seriesData.labels.map((_, i) => i >= seriesData.todayIndex ? seriesData.upperBound[i - seriesData.todayIndex] : null);
  forecastChartInstance.data.datasets[4].data = seriesData.labels.map((_, i) => i >= seriesData.todayIndex ? seriesData.lowerBound[i - seriesData.todayIndex] : null);
  forecastChartInstance.update();
}

/* ==========================================================================
   ROW 2 RIGHT: GEOGRAPHIC DISTRIBUTION MAP (LEAFLET)
   ========================================================================== */
function initDistributionMap() {
  const mapElement = document.getElementById("leaflet-map");
  if (!mapElement) return;

  // Initialize Leaflet map centered at Hyderabad
  leafletMapInstance = L.map("leaflet-map", {
    center: [17.4200, 78.4400],
    zoom: 11,
    zoomControl: false,
    attributionControl: false
  });

  // Add zoom control in top left corner (as in screenshot)
  L.control.zoom({ position: "topleft" }).addTo(leafletMapInstance);

  // CartoDB Dark Matter tile layer
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    maxZoom: 19,
    subdomains: "abcd"
  }).addTo(leafletMapInstance);

  // Layer groups for markers and heat density circles
  markerLayerGroup = L.layerGroup().addTo(leafletMapInstance);
  heatmapLayerGroup = L.layerGroup().addTo(leafletMapInstance);

  // Map metric dropdown
  const metricSelect = document.getElementById("mapMetricSelect");
  if (metricSelect) {
    metricSelect.addEventListener("change", (e) => {
      currentMapMetric = e.target.value;
      updateMapMarkers();
    });
  }

  // Map tool buttons
  const fitBtn = document.getElementById("mapFitBoundsBtn");
  if (fitBtn) {
    fitBtn.addEventListener("click", () => fitMapToBounds());
  }

  const resetBtn = document.getElementById("mapResetBtn");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      leafletMapInstance.setView([17.4200, 78.4400], 11);
    });
  }

  const heatmapToggleBtn = document.getElementById("mapToggleHeatmapBtn");
  if (heatmapToggleBtn) {
    heatmapToggleBtn.addEventListener("click", () => {
      isHeatmapActive = !isHeatmapActive;
      heatmapToggleBtn.classList.toggle("active", isHeatmapActive);
      updateMapMarkers();
    });
  }

  updateMapMarkers();
}

function getFilteredOutlets() {
  return outletsData.filter(store => {
    // Region filter
    if (currentRegion === "telangana" && store.region !== "Telangana") return false;
    if (currentRegion === "andhra" && store.region !== "Andhra Pradesh") return false;
    if (currentRegion === "hyderabad" && store.city !== "Hyderabad") return false;

    // Channel filter
    if (currentChannel !== "all" && store.channel !== currentChannel) return false;

    return true;
  });
}

function updateMapMarkers() {
  if (!leafletMapInstance || !markerLayerGroup) return;

  markerLayerGroup.clearLayers();
  heatmapLayerGroup.clearLayers();

  const filtered = getFilteredOutlets();

  // Dynamic store counts calculation from dataset
  const activeCount = filtered.filter(s => s.status === "active").length;
  const riskCount = filtered.filter(s => s.stockRisk === "Critical Stockout Risk" || s.stockRisk === "Near-Expiry Risk").length;
  const totalCount = filtered.length;

  const countSummaryEl = document.getElementById("mapOutletSummary");
  if (countSummaryEl) {
    countSummaryEl.innerHTML = `
      <span><strong class="count-badge">${totalCount}</strong> demo outlets displayed</span> · 
      <span><strong class="count-badge">${activeCount}</strong> active</span> · 
      <span><strong class="count-badge risk">${riskCount}</strong> stock-risk alerts</span>
    `;
  }

  // Plot individual outlet markers
  filtered.forEach(store => {
    const typeConfig = OUTLET_TYPES[store.type] || OUTLET_TYPES.exclusive;
    const isRisk = store.stockRisk === "Critical Stockout Risk";

    // Create custom SVG marker icon
    const markerHtml = `
      <div style="
        width: 14px;
        height: 14px;
        background-color: ${isRisk ? "#EF4444" : typeConfig.color};
        border: 2px solid #FFFFFF;
        border-radius: ${typeConfig.shape === "circle" ? "50%" : typeConfig.shape === "diamond" ? "2px" : "3px"};
        transform: ${typeConfig.shape === "diamond" ? "rotate(45deg)" : "none"};
        box-shadow: 0 0 8px ${isRisk ? "rgba(239, 68, 68, 0.8)" : "rgba(0, 0, 0, 0.6)"};
        cursor: pointer;
      "></div>
    `;

    const customIcon = L.divIcon({
      className: "custom-outlet-marker",
      html: markerHtml,
      iconSize: [14, 14],
      iconAnchor: [7, 7]
    });

    const marker = L.marker([store.lat, store.lng], { icon: customIcon });

    // Detailed dark popup
    const popupContent = `
      <div class="map-popup-header">
        <div>
          <div class="map-popup-title">${store.name}</div>
          <div class="map-popup-id">${store.id} · ${store.locality}, ${store.city}</div>
        </div>
        <span class="map-popup-type" style="background-color: ${typeConfig.color}25; color: ${typeConfig.color};">
          ${typeConfig.shortLabel}
        </span>
      </div>
      <div class="map-popup-grid">
        <div class="popup-stat">
          <span class="popup-stat-label">Distributor</span>
          <span class="popup-stat-val">${store.distributorId}</span>
        </div>
        <div class="popup-stat">
          <span class="popup-stat-label">Stock Status</span>
          <span class="popup-stat-val" style="color: ${store.stockRisk === 'Critical Stockout Risk' ? '#F87171' : '#34D399'}">
            ${store.stockRisk}
          </span>
        </div>
        <div class="popup-stat">
          <span class="popup-stat-label">SKUs Carried</span>
          <span class="popup-stat-val">${store.skusCarried} Lines</span>
        </div>
        <div class="popup-stat">
          <span class="popup-stat-label">Last Stock Update</span>
          <span class="popup-stat-val">${store.lastUpdate}</span>
        </div>
      </div>
      <div style="margin-top: 8px; display: flex; gap: 6px;">
        <button class="btn btn-primary" style="padding: 3px 8px; font-size: 10px;" onclick="triggerQuickOrder('${store.id}')">
          Order Replenishment
        </button>
      </div>
    `;

    marker.bindPopup(popupContent, { maxWidth: 280 });
    markerLayerGroup.addLayer(marker);

    // If heatmap toggle is on, add density circles
    if (isHeatmapActive) {
      const radius = isRisk ? 900 : 650;
      const color = isRisk ? "#EF4444" : "#F59E0B";
      const circle = L.circle([store.lat, store.lng], {
        radius: radius,
        color: "transparent",
        fillColor: color,
        fillOpacity: 0.18
      });
      heatmapLayerGroup.addLayer(circle);
    }
  });
}

function fitMapToBounds() {
  const filtered = getFilteredOutlets();
  if (filtered.length === 0 || !leafletMapInstance) return;
  const latLngs = filtered.map(s => [s.lat, s.lng]);
  leafletMapInstance.fitBounds(L.latLngBounds(latLngs), { padding: [25, 25] });
}

/* ==========================================================================
   ROW 3 LEFT: TOP SKUS - FORECAST VS ACTUAL
   ========================================================================== */
function initSkuTable() {
  renderSkuTable();
}

function renderSkuTable() {
  const tbody = document.getElementById("topSkusTableBody");
  if (!tbody) return;

  // Show top 5 SKUs on Overview
  const topFive = AMUL_SKUS.slice(0, 5);

  tbody.innerHTML = topFive.map(sku => `
    <tr onclick="selectSkuFromTable('${sku.sku_id}')" style="cursor: pointer;">
      <td>
        <div class="sku-cell">
          <div class="sku-icon-box">${sku.icon}</div>
          <div class="sku-meta">
            <span class="sku-code">${sku.sku_id}</span>
            <span class="sku-name">${sku.short_name}</span>
          </div>
        </div>
      </td>
      <td><span class="category-tag">${sku.category}</span></td>
      <td style="font-weight: 500;">${sku.forecast_units.toLocaleString()}</td>
      <td style="font-weight: 500;">${sku.actual_units.toLocaleString()}</td>
      <td><span class="mape-val">${sku.accuracy_mape}%</span></td>
      <td><span class="yoy-val">+${sku.vs_last_year}%</span></td>
    </tr>
  `).join("");
}

function selectSkuFromTable(skuId) {
  currentSkuId = skuId;
  const select = document.getElementById("forecastSkuSelect");
  if (select) select.value = skuId;
  updateForecastChart();
}

/* ==========================================================================
   ROW 3 RIGHT: REPLENISHMENT AGENT SUGGESTIONS
   ========================================================================== */
function initReplenishmentPanel() {
  renderReplenishmentCards();
}

function renderReplenishmentCards() {
  const container = document.getElementById("replenishmentSuggestionsList");
  if (!container) return;

  // Filter pending review items
  const displayItems = replenishmentData.filter(r => r.status === "Pending Review").slice(0, 3);

  if (displayItems.length === 0) {
    container.innerHTML = `
      <div style="padding: 24px 12px; text-align: center; color: var(--text-muted); font-size: 12px;">
        ✓ All current replenishment suggestions have been reviewed and processed.
      </div>
    `;
    return;
  }

  container.innerHTML = displayItems.map(item => {
    let iconClass = "critical";
    let iconSymbol = "⚠";
    let pillClass = "risk";
    let unitsClass = "order";
    let actionPrefix = "Order";

    if (item.tag === "Increase") {
      iconClass = "warning";
      iconSymbol = "📦";
      pillClass = "increase";
      unitsClass = "warning-order";
      actionPrefix = "Order";
    } else if (item.tag === "Reduce") {
      iconClass = "optimization";
      iconSymbol = "↺";
      pillClass = "reduce";
      unitsClass = "adjust";
      actionPrefix = "Adjust";
    }

    return `
      <div class="suggestion-card" onclick="openReplenishmentModal('${item.id}')">
        <div class="sugg-left">
          <div class="sugg-status-icon ${iconClass}">${iconSymbol}</div>
          <div class="sugg-details">
            <span class="sugg-title">${item.sku_id} - ${item.product_name}</span>
            <span class="sugg-subtitle">${item.store_name} (${item.location})</span>
            <div class="sugg-tag-row">
              <span class="sugg-pill ${pillClass}">${item.tag}</span>
            </div>
          </div>
        </div>
        <div class="sugg-right">
          <div class="sugg-action-info">
            <span class="sugg-action-type">${actionPrefix}</span>
            <span class="sugg-units ${unitsClass}">${item.reorder_qty > 0 ? "+" : ""}${item.reorder_qty.toLocaleString()} Units</span>
            <span class="sugg-deadline">By ${item.deadline}</span>
          </div>
          <span class="chevron-icon">›</span>
        </div>
      </div>
    `;
  }).join("");
}

/* ==========================================================================
   REPLENISHMENT MODAL & DECISION WORKFLOW
   ========================================================================== */
let activeReviewItem = null;

function openReplenishmentModal(suggestionId) {
  activeReviewItem = replenishmentData.find(r => r.id === suggestionId);
  if (!activeReviewItem) return;

  const modal = document.getElementById("replenishmentReviewModal");
  if (!modal) return;

  document.getElementById("modalSkuTitle").textContent = `${activeReviewItem.sku_id} - ${activeReviewItem.product_name}`;
  document.getElementById("modalStoreName").textContent = `${activeReviewItem.store_name} · ${activeReviewItem.location}`;
  document.getElementById("modalPhysicalStock").textContent = `${activeReviewItem.physical_stock.toLocaleString()} Units`;
  document.getElementById("modalTargetStock").textContent = `${activeReviewItem.target_stock.toLocaleString()} Units`;
  document.getElementById("modalLeadTime").textContent = `${activeReviewItem.lead_time_days} Day(s)`;
  document.getElementById("modalReasonText").textContent = activeReviewItem.reason;
  
  const qtyInput = document.getElementById("modalReorderQtyInput");
  if (qtyInput) qtyInput.value = Math.abs(activeReviewItem.reorder_qty);

  modal.classList.add("active");
}

function closeReplenishmentModal() {
  const modal = document.getElementById("replenishmentReviewModal");
  if (modal) modal.classList.remove("active");
  activeReviewItem = null;
}

function approveCurrentSuggestion() {
  if (!activeReviewItem) return;
  const qtyInput = document.getElementById("modalReorderQtyInput");
  const approvedQty = qtyInput ? parseInt(qtyInput.value) : activeReviewItem.reorder_qty;

  activeReviewItem.status = "Approved";
  activeReviewItem.reorder_qty = approvedQty;
  activeReviewItem.decision_log = `Approved by Area Sales Manager on ${new Date().toLocaleTimeString()}`;

  setStoredData(STORAGE_KEYS.REPLENISHMENT, replenishmentData);
  closeReplenishmentModal();
  renderReplenishmentCards();
  if (currentActivePage === "replenishment") renderFullReplenishmentPage();
  showToast(`Replenishment Order ${activeReviewItem.id} Approved (${approvedQty} units).`);
}

function rejectCurrentSuggestion() {
  if (!activeReviewItem) return;
  activeReviewItem.status = "Rejected";
  activeReviewItem.decision_log = `Rejected on ${new Date().toLocaleTimeString()} - Manual override`;

  setStoredData(STORAGE_KEYS.REPLENISHMENT, replenishmentData);
  closeReplenishmentModal();
  renderReplenishmentCards();
  if (currentActivePage === "replenishment") renderFullReplenishmentPage();
  showToast(`Suggestion ${activeReviewItem.id} Rejected.`);
}

function triggerQuickOrder(storeId) {
  const store = outletsData.find(s => s.id === storeId);
  if (!store) return;
  showToast(`Initiating priority dispatch for ${store.name}...`);
  setTimeout(() => {
    showToast(`Order #ORD-${Math.floor(1000 + Math.random() * 9000)} queued for delivery.`);
  }, 600);
}

/* ==========================================================================
   ADDITIONAL 9 FUNCTIONAL SUB-PAGES
   ========================================================================== */
function initAdditionalPages() {
  // Setup interactive tabs, weight sliders, and exports
}

// 1. REPLENISHMENT FULL PAGE (ARS)
function renderFullReplenishmentPage() {
  const container = document.getElementById("fullReplenishmentGrid");
  if (!container) return;

  container.innerHTML = `
    <div class="card-panel">
      <div class="card-panel-header">
        <div class="card-panel-title">Automatic Replenishment System (ARS) Queue</div>
        <div class="panel-controls">
          <span style="font-size: 11px; color: var(--text-muted);">
            Transparent formula: <code>Reorder Qty = max(0, Target Stock - Physical Stock)</code>
          </span>
        </div>
      </div>
      <div class="sku-table-container">
        <table class="compact-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>SKU & Product</th>
              <th>Destination Store</th>
              <th>Physical Stock</th>
              <th>Target Stock</th>
              <th>Reorder Units</th>
              <th>Lead Time</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${replenishmentData.map(r => `
              <tr>
                <td><span style="font-family: monospace; color: var(--text-muted);">${r.id}</span></td>
                <td><strong>${r.product_name}</strong></td>
                <td>${r.store_name}</td>
                <td>${r.physical_stock.toLocaleString()}</td>
                <td>${r.target_stock.toLocaleString()}</td>
                <td><strong style="color: ${r.reorder_qty > 0 ? '#EF4444' : '#10B981'}">${r.reorder_qty.toLocaleString()}</strong></td>
                <td>${r.lead_time_days}d</td>
                <td>
                  <span style="
                    font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px;
                    background: ${r.status === 'Approved' ? 'rgba(16, 185, 129, 0.2)' : r.status === 'Rejected' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)'};
                    color: ${r.status === 'Approved' ? '#6EE7B7' : r.status === 'Rejected' ? '#FCA5A5' : '#FCD34D'};
                  ">
                    ${r.status}
                  </span>
                </td>
                <td>
                  ${r.status === 'Pending Review' ? `
                    <button class="btn btn-primary" style="padding: 2px 7px; font-size: 10.5px;" onclick="openReplenishmentModal('${r.id}')">
                      Review
                    </button>
                  ` : `
                    <span style="font-size: 10px; color: var(--text-muted);">${r.decision_log || 'Processed'}</span>
                  `}
                </td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 2. CHANNEL ECONOMICS PAGE (6 Channels Waterfall & Calculator)
function renderChannelEconomicsPage() {
  const container = document.getElementById("view-economics");
  if (!container) return;

  container.innerHTML = `
    <div class="kpi-row" style="grid-template-columns: repeat(3, 1fr); margin-bottom: 14px;">
      <div class="kpi-card">
        <div class="kpi-title">GCMMF Turnover (FY2025–26) [V]</div>
        <div class="kpi-main-metric" style="color: #38BDF8;">₹73,450 Cr</div>
        <div class="kpi-footer"><span>+11.4% YoY · Verified GCMMF PTI Report</span></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Amul Brand Turnover [V]</div>
        <div class="kpi-main-metric" style="color: #38BDF8;">₹100,000+ Cr</div>
        <div class="kpi-footer"><span>Unduplicated brand-level turnover</span></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Investment Mix Status [PT]</div>
        <div class="kpi-main-metric" style="color: #FBBF24;">6 Channels</div>
        <div class="kpi-footer"><span>Playbook proposed planning mix (not historical revenue)</span></div>
      </div>
    </div>

    <div class="card-panel">
      <div class="card-panel-header">
        <div class="card-panel-title">Playbook Section 3.4: Channel Contribution Margin Waterfall</div>
        <span style="font-size: 11px; color: var(--text-muted);">
          Formula: Realisation - Product Cost - Channel Margin - Promos - Logistics - Cold Chain - Wastage = Net Contribution
        </span>
      </div>
      <div class="sku-table-container">
        <table class="compact-table">
          <thead>
            <tr>
              <th>Channel Name</th>
              <th>Proposed Mix</th>
              <th>Product Cost</th>
              <th>Distributor Margin</th>
              <th>Promos</th>
              <th>Cold-Chain Cost</th>
              <th>Returns & Wastage</th>
              <th>Est. Contribution</th>
              <th>Evidence Status</th>
            </tr>
          </thead>
          <tbody>
            ${channelEconomicsData.map(ch => `
              <tr>
                <td><strong>${ch.channel}</strong></td>
                <td><span style="font-weight: 600; color: #38BDF8;">${ch.proposed_allocation}%</span></td>
                <td>${ch.product_cost}%</td>
                <td>${ch.channel_distributor_margin}%</td>
                <td>${ch.discounts_promotions}%</td>
                <td>${ch.cold_chain_cost}%</td>
                <td>${ch.returns_expiry_wastage}%</td>
                <td>
                  <strong style="color: ${ch.estimated_contribution > 0 ? '#10B981' : '#EF4444'}">
                    ${ch.estimated_contribution > 0 ? '+' : ''}${ch.estimated_contribution}%
                  </strong>
                </td>
                <td><span style="font-size: 10px; color: var(--text-muted);">${ch.evidence_status}</span></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 3. MARKET PRIORITISATION PAGE (Playbook Section 3.5 Weighted Model)
let marketWeights = {
  demand: 25,
  whitespace: 25,
  channel: 20,
  coldChain: 15,
  dataQuality: 15
};

function renderMarketPrioritisationPage() {
  const container = document.getElementById("view-prioritisation");
  if (!container) return;

  // Calculate composite city scores based on current weights
  const scoredCities = marketCitiesData.map(c => {
    const totalScore = (
      (c.demand_score * marketWeights.demand) +
      (c.whitespace_score * marketWeights.whitespace) +
      (c.channel_readiness * marketWeights.channel) +
      (c.cold_chain_readiness * marketWeights.coldChain) +
      (c.data_quality_score * marketWeights.dataQuality)
    ) / 100.0;
    return { ...c, compositeScore: totalScore.toFixed(1) };
  }).sort((a, b) => b.compositeScore - a.compositeScore);

  container.innerHTML = `
    <div class="card-panel" style="margin-bottom: 14px;">
      <div class="card-panel-header">
        <div class="card-panel-title">Configurable Prioritisation Weights [TA/PT]</div>
        <span style="font-size: 11px; color: var(--text-muted);">Adjust weights to dynamically recalculate expansion readiness</span>
      </div>
      <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; padding: 6px 0;">
        <div>
          <label style="font-size: 11px; color: var(--text-secondary); display: block; margin-bottom: 4px;">
            Demand Potential (${marketWeights.demand}%)
          </label>
          <input type="range" min="5" max="50" value="${marketWeights.demand}" style="width: 100%; accent-color: var(--amul-red);" 
            oninput="updateMarketWeight('demand', this.value)">
        </div>
        <div>
          <label style="font-size: 11px; color: var(--text-secondary); display: block; margin-bottom: 4px;">
            Whitespace Gap (${marketWeights.whitespace}%)
          </label>
          <input type="range" min="5" max="50" value="${marketWeights.whitespace}" style="width: 100%; accent-color: var(--amul-red);" 
            oninput="updateMarketWeight('whitespace', this.value)">
        </div>
        <div>
          <label style="font-size: 11px; color: var(--text-secondary); display: block; margin-bottom: 4px;">
            Channel Readiness (${marketWeights.channel}%)
          </label>
          <input type="range" min="5" max="50" value="${marketWeights.channel}" style="width: 100%; accent-color: var(--amul-red);" 
            oninput="updateMarketWeight('channel', this.value)">
        </div>
        <div>
          <label style="font-size: 11px; color: var(--text-secondary); display: block; margin-bottom: 4px;">
            Cold-Chain Capacity (${marketWeights.coldChain}%)
          </label>
          <input type="range" min="5" max="50" value="${marketWeights.coldChain}" style="width: 100%; accent-color: var(--amul-red);" 
            oninput="updateMarketWeight('coldChain', this.value)">
        </div>
        <div>
          <label style="font-size: 11px; color: var(--text-secondary); display: block; margin-bottom: 4px;">
            Data Quality & DMS (${marketWeights.dataQuality}%)
          </label>
          <input type="range" min="5" max="50" value="${marketWeights.dataQuality}" style="width: 100%; accent-color: var(--amul-red);" 
            oninput="updateMarketWeight('dataQuality', this.value)">
        </div>
      </div>
    </div>

    <div class="card-panel">
      <div class="card-panel-header">
        <div class="card-panel-title">Candidate City Prioritisation Ranking (Telangana & Andhra Pradesh)</div>
        <span style="font-size: 11px; color: #F59E0B;">Notice: Planning model only; does not claim verified Amul city revenue ranking</span>
      </div>
      <div class="sku-table-container">
        <table class="compact-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>City / Urban Agglomeration</th>
              <th>State</th>
              <th>Tier</th>
              <th>Demand</th>
              <th>Whitespace</th>
              <th>Channel</th>
              <th>Cold Chain</th>
              <th>Data Quality</th>
              <th>Readiness Score</th>
              <th>Pilot Status</th>
            </tr>
          </thead>
          <tbody>
            ${scoredCities.map((city, idx) => `
              <tr>
                <td><strong style="color: ${idx < 2 ? '#E53935' : '#94A3B8'};">#${idx + 1}</strong></td>
                <td><strong>${city.city}</strong></td>
                <td>${city.state}</td>
                <td><span class="category-tag">${city.tier}</span></td>
                <td>${city.demand_score}</td>
                <td>${city.whitespace_score}</td>
                <td>${city.channel_readiness}</td>
                <td>${city.cold_chain_readiness}</td>
                <td>${city.data_quality_score}</td>
                <td><strong style="font-size: 13px; color: #10B981;">${city.compositeScore}</strong></td>
                <td>
                  <span style="
                    font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px;
                    background: ${city.pilot_recommended ? 'rgba(229, 57, 53, 0.2)' : 'rgba(255, 255, 255, 0.06)'};
                    color: ${city.pilot_recommended ? '#F87171' : '#64748B'};
                  ">
                    ${city.pilot_recommended ? '10-Week Pilot' : 'Stage 2 Rollout'}
                  </span>
                </td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function updateMarketWeight(key, val) {
  marketWeights[key] = parseInt(val);
  renderMarketPrioritisationPage();
}

// 4. INVENTORY REGIMES PAGE
function renderInventoryPage() {
  const container = document.getElementById("view-inventory");
  if (!container) return;

  container.innerHTML = `
    <div class="kpi-row" style="margin-bottom: 14px;">
      ${Object.entries(STORAGE_REGIMES).map(([key, reg]) => `
        <div class="kpi-card" style="border-top: 3px solid ${reg.color};">
          <div class="kpi-title">${reg.name}</div>
          <div class="kpi-main-metric" style="color: ${reg.color}; font-size: 20px;">
            ${reg.tempRange}
          </div>
          <div class="kpi-footer">
            <span>Shelf Life: ${reg.shelfLife}</span>
          </div>
          <div style="font-size: 10px; color: var(--text-muted); margin-top: 6px;">
            ${reg.criticalRisk}
          </div>
        </div>
      `).join("")}
    </div>

    <div class="card-panel">
      <div class="card-panel-header">
        <div class="card-panel-title">Multi-Temperature SKU Inventory & Days of Cover Matrix</div>
      </div>
      <div class="sku-table-container">
        <table class="compact-table">
          <thead>
            <tr>
              <th>SKU ID</th>
              <th>Product Name</th>
              <th>Temperature Regime</th>
              <th>Stock on Hand</th>
              <th>Target Stock</th>
              <th>Days of Cover</th>
              <th>Lead Time</th>
              <th>Risk Level</th>
            </tr>
          </thead>
          <tbody>
            ${AMUL_SKUS.map(s => {
              const daysOfCover = ((s.stock_on_hand / (s.forecast_units / 28)) || 0).toFixed(1);
              return `
                <tr>
                  <td><code>${s.sku_id}</code></td>
                  <td><strong>${s.product_name}</strong></td>
                  <td><span class="category-tag">${STORAGE_REGIMES[s.regime]?.name || s.regime}</span></td>
                  <td>${s.stock_on_hand.toLocaleString()} Units</td>
                  <td>${s.target_stock.toLocaleString()} Units</td>
                  <td><strong>${daysOfCover} Days</strong></td>
                  <td>${s.lead_time_days} Day(s)</td>
                  <td>
                    <span style="color: ${s.stockout_risk === 'High' || s.stockout_risk === 'Critical' ? '#EF4444' : '#10B981'}; font-weight: 600;">
                      ${s.stockout_risk}
                    </span>
                  </td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 5. REPORTS & CSV EXPORT PAGE
function renderReportsPage() {
  const container = document.getElementById("view-reports");
  if (!container) return;

  const filtered = getFilteredOutlets();

  container.innerHTML = `
    <div class="card-panel">
      <div class="card-panel-header">
        <div class="card-panel-title">Distribution Data Export Center</div>
        <div class="panel-controls">
          <button class="btn btn-primary" onclick="exportOutletsCsv()">Download Stores CSV (${filtered.length} Outlets)</button>
          <button class="btn btn-secondary" onclick="exportReplenishmentCsv()">Download Replenishment Queue CSV</button>
        </div>
      </div>
      <p style="font-size: 11.5px; color: var(--text-muted); margin-bottom: 12px;">
        Export active demo records reflecting your current region and channel filters.
      </p>
      <div class="sku-table-container">
        <table class="compact-table">
          <thead>
            <tr>
              <th>Store ID</th>
              <th>Store Name</th>
              <th>Locality</th>
              <th>City</th>
              <th>Type</th>
              <th>Channel</th>
              <th>Status</th>
              <th>Stock Risk</th>
            </tr>
          </thead>
          <tbody>
            ${filtered.slice(0, 10).map(s => `
              <tr>
                <td><code>${s.id}</code></td>
                <td><strong>${s.name}</strong></td>
                <td>${s.locality}</td>
                <td>${s.city}</td>
                <td>${OUTLET_TYPES[s.type]?.shortLabel || s.type}</td>
                <td>${s.channel}</td>
                <td>${s.status}</td>
                <td>${s.stockRisk}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
        <div class="table-footer">
          <span>Showing 10 of ${filtered.length} filtered outlets</span>
        </div>
      </div>
    </div>
  `;
}

function exportOutletsCsv() {
  const filtered = getFilteredOutlets();
  const headers = ["id", "name", "type", "city", "locality", "latitude", "longitude", "status", "channel", "skus_carried", "stock_risk"];
  const rows = filtered.map(s => [
    s.id, `"${s.name}"`, s.type, s.city, `"${s.locality}"`, s.lat, s.lng, s.status, `"${s.channel}"`, s.skusCarried, `"${s.stockRisk}"`
  ]);

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `amul_outlets_filtered_${currentRegion}_${currentChannel}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast("Filtered store census exported successfully.");
}

function exportReplenishmentCsv() {
  const headers = ["id", "sku_id", "product_name", "store_id", "store_name", "physical_stock", "target_stock", "reorder_qty", "status", "deadline"];
  const rows = replenishmentData.map(r => [
    r.id, r.sku_id, `"${r.product_name}"`, r.store_id, `"${r.store_name}"`, r.physical_stock, r.target_stock, r.reorder_qty, r.status, `"${r.deadline}"`
  ]);

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "amul_replenishment_orders.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast("Replenishment recommendations exported.");
}

// 6. ALERTS REGISTER PAGE
function renderAlertsPage() {
  const container = document.getElementById("view-alerts");
  if (!container) return;

  container.innerHTML = `
    <div class="card-panel">
      <div class="card-panel-header">
        <div class="card-panel-title">Central Distribution Alert Register</div>
        <div class="panel-controls">
          <span style="font-size: 11px; color: var(--text-muted);">${alertsData.filter(a => a.status === 'Active').length} Active Alerts</span>
        </div>
      </div>
      <div class="sku-table-container">
        <table class="compact-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Severity</th>
              <th>Category</th>
              <th>Alert Title & Description</th>
              <th>Location</th>
              <th>Time</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${alertsData.map(a => `
              <tr>
                <td><code>${a.id}</code></td>
                <td>
                  <span style="
                    font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px;
                    background: ${a.severity === 'critical' ? 'rgba(239, 68, 68, 0.2)' : a.severity === 'warning' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(56, 189, 248, 0.2)'};
                    color: ${a.severity === 'critical' ? '#FCA5A5' : a.severity === 'warning' ? '#FCD34D' : '#7DD3FC'};
                  ">
                    ${a.severity.toUpperCase()}
                  </span>
                </td>
                <td>${a.category}</td>
                <td>
                  <div style="display: flex; flex-direction: column;">
                    <strong>${a.title}</strong>
                    <span style="font-size: 10.5px; color: var(--text-muted);">${a.message}</span>
                  </div>
                </td>
                <td>${a.storeId}</td>
                <td style="white-space: nowrap; font-size: 10.5px; color: var(--text-muted);">${a.timestamp}</td>
                <td><strong>${a.status}</strong></td>
                <td>
                  ${a.status === 'Active' ? `
                    <button class="btn btn-secondary" style="padding: 2px 7px; font-size: 10px;" onclick="acknowledgeAlert('${a.id}')">
                      Acknowledge
                    </button>
                  ` : a.status === 'Acknowledged' ? `
                    <button class="btn btn-primary" style="padding: 2px 7px; font-size: 10px;" onclick="resolveAlert('${a.id}')">
                      Resolve
                    </button>
                  ` : `
                    <span style="color: #10B981; font-size: 11px;">✓ Resolved</span>
                  `}
                </td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function acknowledgeAlert(alertId) {
  const alert = alertsData.find(a => a.id === alertId);
  if (alert) {
    alert.status = "Acknowledged";
    setStoredData(STORAGE_KEYS.ALERTS, alertsData);
    renderAlertsPage();
    updateAlertCountBadge();
    showToast(`Alert ${alertId} acknowledged.`);
  }
}

function resolveAlert(alertId) {
  const alert = alertsData.find(a => a.id === alertId);
  if (alert) {
    alert.status = "Resolved";
    setStoredData(STORAGE_KEYS.ALERTS, alertsData);
    renderAlertsPage();
    updateAlertCountBadge();
    showToast(`Alert ${alertId} marked resolved.`);
  }
}

function updateAlertCountBadge() {
  const activeCount = alertsData.filter(a => a.status === "Active").length;
  const badges = document.querySelectorAll(".nav-badge");
  badges.forEach(b => {
    b.textContent = activeCount;
    b.style.display = activeCount > 0 ? "inline-block" : "none";
  });
}

/* ==========================================================================
   AI ASSISTANT SLIDE-OUT DRAWER
   ========================================================================== */
function initAiDrawer() {
  const openBtn = document.getElementById("openAiDrawerBtn");
  const closeBtn = document.getElementById("closeAiDrawerBtn");
  const drawer = document.getElementById("aiDrawer");
  const sendBtn = document.getElementById("sendAiMsgBtn");
  const input = document.getElementById("aiDrawerInput");

  if (openBtn && drawer) {
    openBtn.addEventListener("click", () => drawer.classList.add("open"));
  }
  if (closeBtn && drawer) {
    closeBtn.addEventListener("click", () => drawer.classList.remove("open"));
  }

  if (sendBtn && input) {
    sendBtn.addEventListener("click", () => handleAiUserMessage(input));
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") handleAiUserMessage(input);
    });
  }
}

function handleAiUserMessage(input) {
  const text = input.value.trim();
  if (!text) return;

  const messagesContainer = document.getElementById("aiDrawerMessages");
  if (!messagesContainer) return;

  // Add user bubble
  const userDiv = document.createElement("div");
  userDiv.className = "user-bubble";
  userDiv.textContent = text;
  messagesContainer.appendChild(userDiv);
  input.value = "";

  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  // Generate deterministic, evidence-grounded response
  setTimeout(() => {
    const aiDiv = document.createElement("div");
    aiDiv.className = "ai-bubble";

    const lower = text.toLowerCase();
    let reply = "";

    if (lower.includes("turnover") || lower.includes("revenue")) {
      reply = `<strong>Amul Brand vs GCMMF Turnover [V]:</strong><br>
      • FY2025–26 Amul brand turnover exceeded ₹1 lakh crore (~11% growth).<br>
      • GCMMF federation turnover was ₹73,450 crore (+11.4% YoY).<br>
      <em>Note: These are distinct measures. Do not add them or treat them as channel revenue.</em>`;
    } else if (lower.includes("replenishment") || lower.includes("formula")) {
      reply = `<strong>Replenishment Engine Formula [TA/PT]:</strong><br>
      <code>Recommended quantity = max(0, Target Stock - Physical Stock)</code><br>
      In the 2026 GCMMF Anand field study, distributor ARS incorporates lead time, minimum order pack sizes, and temperature-regime shelf life buffers.`;
    } else if (lower.includes("channel") || lower.includes("margin")) {
      reply = `<strong>Channel Economics Architecture [PT]:</strong><br>
      Proposed planning mix totals 100%: General Trade (50%), Modern Trade (17%), Amul Outlets (13%), E-commerce (8%), Quick Commerce (7%), and Institutional/HoReCa (5%).<br>
      <em>Boundary: Third-party margin ranges are indicative; confirm actual terms before commercial investment decisions.</em>`;
    } else {
      reply = `<strong>Distribution Intelligence Summary:</strong><br>
      Currently tracking 128 seeded outlets across Telangana and Andhra Pradesh. 
      Morning pouch milk availability stands at 98.1% with active ARS reviews queued for 6 priority distribution corridors.`;
    }

    aiDiv.innerHTML = reply;
    messagesContainer.appendChild(aiDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }, 450);
}

function askAiPreset(questionText) {
  const drawer = document.getElementById("aiDrawer");
  const input = document.getElementById("aiDrawerInput");
  if (drawer) drawer.classList.add("open");
  if (input) {
    input.value = questionText;
    handleAiUserMessage(input);
  }
}

/* ==========================================================================
   TOAST NOTIFICATION HELPER
   ========================================================================== */
function showToast(msg) {
  let toast = document.getElementById("dashboardToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "dashboardToast";
    toast.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: rgba(19, 23, 34, 0.95);
      border: 1px solid rgba(229, 57, 53, 0.4);
      border-left: 4px solid #E53935;
      color: #FFFFFF;
      padding: 10px 16px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
      z-index: 2000;
      transition: opacity 0.25s, transform 0.25s;
    `;
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.opacity = "1";
  toast.style.transform = "translateY(0)";

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
  }, 3200);
}

function setupEventListeners() {
  // Global shortcuts or window resize
  window.addEventListener("resize", () => {
    if (leafletMapInstance) leafletMapInstance.invalidateSize();
    if (forecastChartInstance) forecastChartInstance.resize();
  });
}

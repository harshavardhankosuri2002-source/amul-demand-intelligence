/**
 * AMUL DISTRIBUTION INTELLIGENCE - CORE DATA ARCHITECTURE
 * Grounded in the GCMMF Integrated Sales & Distribution Strategy Playbook (MBA 2025-27)
 * Evidence-labeled: [V] Verified, [3P] Third-party, [TA] Team Analysis, [PT] Proposed Target
 * Deterministic synthetic demo records for operational decision-support in Telangana & AP markets.
 */

// Storage regime definitions
const STORAGE_REGIMES = {
  fresh: {
    name: "Fresh Dairy",
    tempRange: "2°C to 4°C",
    shelfLife: "2 - 14 Days",
    criticalRisk: "Rapid morning stockouts & souring write-offs",
    color: "#EF4444",
    bgAlpha: "rgba(239, 68, 68, 0.15)"
  },
  chilled: {
    name: "Chilled Dairy",
    tempRange: "0°C to 4°C",
    shelfLife: "180 - 240 Days",
    criticalRisk: "Cold-chain breaks cause fat separation & weeping",
    color: "#F59E0B",
    bgAlpha: "rgba(245, 158, 11, 0.15)"
  },
  frozen: {
    name: "Deep Frozen",
    tempRange: "-18°C or below",
    shelfLife: "360 Days",
    criticalRisk: "Thermal cycling crystallisation & meltdown",
    color: "#3B82F6",
    bgAlpha: "rgba(59, 130, 246, 0.15)"
  },
  ambient: {
    name: "Ambient Dairy",
    tempRange: "Room Temperature",
    shelfLife: "180 - 365 Days",
    criticalRisk: "Packaging denting & festive demand surges",
    color: "#10B981",
    bgAlpha: "rgba(16, 185, 129, 0.15)"
  }
};

// SKU Catalog (14 core strategic SKUs across 4 temperature regimes)
const AMUL_SKUS = [
  {
    sku_id: "AMUL-FRSH-001",
    product_name: "Amul Taaza Toned Milk (1L Pouch)",
    short_name: "Taaza Milk 1L",
    category: "Fresh Milk",
    regime: "fresh",
    mrp: 54.0,
    unit_cost: 46.0,
    forecast_units: 196524,
    actual_units: 190821,
    accuracy_mape: 3.2,
    vs_last_year: 24.0,
    stockout_risk: "High",
    stock_on_hand: 4820,
    target_stock: 12500,
    lead_time_days: 1,
    shelf_life_days: 2,
    icon: "🥛"
  },
  {
    sku_id: "AMUL-FRSH-002",
    product_name: "Amul Gold Full Cream Milk (500ml Pouch)",
    short_name: "Gold Milk 500ml",
    category: "Fresh Milk",
    regime: "fresh",
    mrp: 33.0,
    unit_cost: 28.0,
    forecast_units: 128765,
    actual_units: 132950,
    accuracy_mape: 4.7,
    vs_last_year: 18.0,
    stockout_risk: "Moderate",
    stock_on_hand: 6150,
    target_stock: 9800,
    lead_time_days: 1,
    shelf_life_days: 2,
    icon: "🥛"
  },
  {
    sku_id: "AMUL-FRSH-003",
    product_name: "Amul Masti Dahi (400g Cup)",
    short_name: "Masti Dahi 400g",
    category: "Curd & Fermented",
    regime: "fresh",
    mrp: 35.0,
    unit_cost: 27.0,
    forecast_units: 87665,
    actual_units: 85001,
    accuracy_mape: 3.1,
    vs_last_year: 9.0,
    stockout_risk: "Low",
    stock_on_hand: 3840,
    target_stock: 5200,
    lead_time_days: 2,
    shelf_life_days: 10,
    icon: "🥣"
  },
  {
    sku_id: "AMUL-FRSH-004",
    product_name: "Amul Fresh Malai Paneer (200g Block)",
    short_name: "Malai Paneer 200g",
    category: "Fresh Dairy",
    regime: "fresh",
    mrp: 92.0,
    unit_cost: 74.0,
    forecast_units: 76432,
    actual_units: 74881,
    accuracy_mape: 2.0,
    vs_last_year: 15.0,
    stockout_risk: "Critical",
    stock_on_hand: 1420,
    target_stock: 4600,
    lead_time_days: 2,
    shelf_life_days: 14,
    icon: "🧈"
  },
  {
    sku_id: "AMUL-CHIL-001",
    product_name: "Amul Pasteurised Butter (500g Carton)",
    short_name: "Amul Butter 500g",
    category: "Butter",
    regime: "chilled",
    mrp: 275.0,
    unit_cost: 225.0,
    forecast_units: 112354,
    actual_units: 108213,
    accuracy_mape: 3.7,
    vs_last_year: 12.0,
    stockout_risk: "Moderate",
    stock_on_hand: 5200,
    target_stock: 8500,
    lead_time_days: 4,
    shelf_life_days: 180,
    icon: "🧈"
  },
  {
    sku_id: "AMUL-CHIL-002",
    product_name: "Amul Processed Cheese Blocks (500g)",
    short_name: "Cheese Block 500g",
    category: "Cheese",
    regime: "chilled",
    mrp: 290.0,
    unit_cost: 235.0,
    forecast_units: 64200,
    actual_units: 61890,
    accuracy_mape: 3.6,
    vs_last_year: 16.5,
    stockout_risk: "Low",
    stock_on_hand: 4100,
    target_stock: 6000,
    lead_time_days: 4,
    shelf_life_days: 240,
    icon: "🧀"
  },
  {
    sku_id: "AMUL-CHIL-003",
    product_name: "Amul Cheese Slices (200g 10 Slices)",
    short_name: "Cheese Slices 200g",
    category: "Cheese",
    regime: "chilled",
    mrp: 145.0,
    unit_cost: 115.0,
    forecast_units: 82100,
    actual_units: 79450,
    accuracy_mape: 3.2,
    vs_last_year: 14.0,
    stockout_risk: "Low",
    stock_on_hand: 5900,
    target_stock: 7500,
    lead_time_days: 3,
    shelf_life_days: 180,
    icon: "🧀"
  },
  {
    sku_id: "AMUL-FROZ-001",
    product_name: "Amul Real Ice Cream Vanilla Magic (1L Tub)",
    short_name: "Vanilla Ice Cream 1L",
    category: "Ice Cream",
    regime: "frozen",
    mrp: 160.0,
    unit_cost: 118.0,
    forecast_units: 95400,
    actual_units: 91200,
    accuracy_mape: 4.4,
    vs_last_year: 21.0,
    stockout_risk: "High",
    stock_on_hand: 3100,
    target_stock: 7200,
    lead_time_days: 5,
    shelf_life_days: 360,
    icon: "🍨"
  },
  {
    sku_id: "AMUL-FROZ-002",
    product_name: "Amul Choco-Chips Ice Cream Tub (1L)",
    short_name: "Choco-Chips Tub 1L",
    category: "Ice Cream",
    regime: "frozen",
    mrp: 240.0,
    unit_cost: 175.0,
    forecast_units: 68300,
    actual_units: 66100,
    accuracy_mape: 3.2,
    vs_last_year: 28.0,
    stockout_risk: "Moderate",
    stock_on_hand: 2400,
    target_stock: 4800,
    lead_time_days: 5,
    shelf_life_days: 360,
    icon: "🍨"
  },
  {
    sku_id: "AMUL-FROZ-003",
    product_name: "Amul Frozen Green Peas (500g Pouch)",
    short_name: "Green Peas 500g",
    category: "Frozen Veg",
    regime: "frozen",
    mrp: 85.0,
    unit_cost: 62.0,
    forecast_units: 54100,
    actual_units: 52800,
    accuracy_mape: 2.4,
    vs_last_year: 11.0,
    stockout_risk: "Low",
    stock_on_hand: 4300,
    target_stock: 5500,
    lead_time_days: 6,
    shelf_life_days: 365,
    icon: "🥦"
  },
  {
    sku_id: "AMUL-AMBI-001",
    product_name: "Amul Pure Cow Ghee (1L Tin)",
    short_name: "Cow Ghee 1L Tin",
    category: "Ghee",
    regime: "ambient",
    mrp: 630.0,
    unit_cost: 525.0,
    forecast_units: 61200,
    actual_units: 59400,
    accuracy_mape: 2.9,
    vs_last_year: 19.5,
    stockout_risk: "Low",
    stock_on_hand: 8900,
    target_stock: 8000,
    lead_time_days: 6,
    shelf_life_days: 270,
    icon: "🥫"
  },
  {
    sku_id: "AMUL-AMBI-002",
    product_name: "Amul Kool Kesar Badam (200ml Can)",
    short_name: "Kool Kesar Badam 200ml",
    category: "Beverages",
    regime: "ambient",
    mrp: 35.0,
    unit_cost: 26.0,
    forecast_units: 142000,
    actual_units: 138500,
    accuracy_mape: 2.5,
    vs_last_year: 31.0,
    stockout_risk: "Moderate",
    stock_on_hand: 12400,
    target_stock: 18000,
    lead_time_days: 4,
    shelf_life_days: 180,
    icon: "🧃"
  },
  {
    sku_id: "AMUL-AMBI-003",
    product_name: "Amul Mithai Mate Condensed Milk (400g)",
    short_name: "Mithai Mate 400g",
    category: "Ambient Dairy",
    regime: "ambient",
    mrp: 140.0,
    unit_cost: 108.0,
    forecast_units: 41200,
    actual_units: 40100,
    accuracy_mape: 2.7,
    vs_last_year: 8.0,
    stockout_risk: "Low",
    stock_on_hand: 6100,
    target_stock: 6500,
    lead_time_days: 5,
    shelf_life_days: 365,
    icon: "🥛"
  },
  {
    sku_id: "AMUL-AMBI-004",
    product_name: "Amul Dark Chocolate (150g Bar)",
    short_name: "Dark Chocolate 150g",
    category: "Chocolates",
    regime: "ambient",
    mrp: 110.0,
    unit_cost: 80.0,
    forecast_units: 49500,
    actual_units: 47800,
    accuracy_mape: 3.4,
    vs_last_year: 22.0,
    stockout_risk: "Low",
    stock_on_hand: 7200,
    target_stock: 8000,
    lead_time_days: 5,
    shelf_life_days: 365,
    icon: "🍫"
  }
];

// Outlet Types Configuration
const OUTLET_TYPES = {
  exclusive: {
    label: "Amul Parlours / Exclusive Outlets",
    shortLabel: "Amul Parlour",
    color: "#E53935", // Red
    iconSymbol: "◆",
    shape: "diamond",
    description: "Company-approved dedicated parlours, COE outlets, and scooping booths"
  },
  general_trade: {
    label: "General Trade Retailers (Kiranas)",
    shortLabel: "General Trade",
    color: "#F59E0B", // Amber
    iconSymbol: "●",
    shape: "circle",
    description: "Neighbourhood mom-and-pop grocery stores with morning milk delivery"
  },
  modern_trade: {
    label: "Modern Trade / Supermarkets",
    shortLabel: "Modern Trade",
    color: "#3B82F6", // Blue
    iconSymbol: "■",
    shape: "square",
    description: "Supermarket chains (Ratnadeep, D-Mart, Spencer's, Reliance Smart)"
  },
  quick_commerce: {
    label: "Quick-Commerce Fulfilment Points",
    shortLabel: "Quick Commerce",
    color: "#8B5CF6", // Purple
    iconSymbol: "⬡",
    shape: "hexagon",
    description: "Dark stores (Blinkit, Swiggy Instamart, Zepto) with rapid 10-15m dispatch"
  },
  distributor: {
    label: "Distributor / Stockist Locations",
    shortLabel: "Distributor Depot",
    color: "#06B6D4", // Cyan
    iconSymbol: "▲",
    shape: "triangle",
    description: "Wholesale stockists and multi-temperature redistribution hubs"
  },
  institutional: {
    label: "Institutional / HoReCa Customers",
    shortLabel: "HoReCa / B2B",
    color: "#10B981", // Emerald
    iconSymbol: "★",
    shape: "star",
    description: "Hotels, corporate canteens, bakeries, and educational institutions"
  }
};

// Seeded 128 Stores Dataset across Hyderabad and Telangana / AP markets
// Deterministic coordinates in real commercial corridors
const INITIAL_OUTLETS = [
  // --- HYDERABAD & SECUNDERABAD METRO (70 Outlets) ---
  // Gachibowli & Hitec City (IT Corridor)
  { id: "STR-HYD-1001", name: "Cyber Towers Exclusive Parlour", type: "exclusive", city: "Hyderabad", locality: "Hitec City", lat: 17.4504, lng: 78.3808, status: "active", distributorId: "DIST-HYD-WEST", channel: "Amul Parlours", skusCarried: 42, lastUpdate: "10 mins ago", stockRisk: "None", currentStock: 3400, targetStock: 3500 },
  { id: "STR-HYD-1002", name: "Gachibowli DLF Quick-Hub", type: "quick_commerce", city: "Hyderabad", locality: "Gachibowli", lat: 17.4478, lng: 78.3564, status: "active", distributorId: "DIST-HYD-WEST", channel: "Quick Commerce", skusCarried: 38, lastUpdate: "5 mins ago", stockRisk: "Critical Stockout Risk", currentStock: 420, targetStock: 2200 },
  { id: "STR-HYD-1003", name: "Ratnadeep Supermarket Gachibowli", type: "modern_trade", city: "Hyderabad", locality: "Gachibowli", lat: 17.4412, lng: 78.3619, status: "active", distributorId: "DIST-HYD-WEST", channel: "Modern Trade", skusCarried: 54, lastUpdate: "1 hour ago", stockRisk: "None", currentStock: 4800, targetStock: 5000 },
  { id: "STR-HYD-1004", name: "Sri Laxmi Kirana General Store", type: "general_trade", city: "Hyderabad", locality: "Gachibowli", lat: 17.4385, lng: 78.3688, status: "active", distributorId: "DIST-HYD-WEST", channel: "General Trade", skusCarried: 18, lastUpdate: "2 hours ago", stockRisk: "None", currentStock: 950, targetStock: 1100 },
  { id: "STR-HYD-1005", name: "Woxsen University Executive Canteen", type: "institutional", city: "Hyderabad", locality: "Sangareddy / Outer", lat: 17.6599, lng: 78.0289, status: "active", distributorId: "DIST-HYD-NORTH", channel: "Institutional / HoReCa", skusCarried: 24, lastUpdate: "3 hours ago", stockRisk: "None", currentStock: 2200, targetStock: 2500 },
  { id: "STR-HYD-1006", name: "West Hyd Cold Depot (Stockist)", type: "distributor", city: "Hyderabad", locality: "Kondapur", lat: 17.4655, lng: 78.3582, status: "active", distributorId: "DIST-HYD-WEST", channel: "Distributor / Stockist", skusCarried: 110, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 34500, targetStock: 35000 },
  { id: "STR-HYD-1007", name: "Kondapur Zepto Dark Store", type: "quick_commerce", city: "Hyderabad", locality: "Kondapur", lat: 17.4712, lng: 78.3621, status: "active", distributorId: "DIST-HYD-WEST", channel: "Quick Commerce", skusCarried: 34, lastUpdate: "15 mins ago", stockRisk: "None", currentStock: 1850, targetStock: 2000 },
  { id: "STR-HYD-1008", name: "Kondapur Heritage Fresh", type: "modern_trade", city: "Hyderabad", locality: "Kondapur", lat: 17.4682, lng: 78.3695, status: "active", distributorId: "DIST-HYD-WEST", channel: "Modern Trade", skusCarried: 48, lastUpdate: "45 mins ago", stockRisk: "None", currentStock: 3800, targetStock: 4000 },
  { id: "STR-HYD-1009", name: "Madhapur D-Mart Ready", type: "modern_trade", city: "Hyderabad", locality: "Madhapur", lat: 17.4485, lng: 78.3908, status: "active", distributorId: "DIST-HYD-WEST", channel: "Modern Trade", skusCarried: 50, lastUpdate: "30 mins ago", stockRisk: "None", currentStock: 5200, targetStock: 5500 },
  { id: "STR-HYD-1010", name: "Ayyappa Society Kirana Provisions", type: "general_trade", city: "Hyderabad", locality: "Madhapur", lat: 17.4528, lng: 78.3889, status: "active", distributorId: "DIST-HYD-WEST", channel: "General Trade", skusCarried: 22, lastUpdate: "4 hours ago", stockRisk: "Critical Stockout Risk", currentStock: 310, targetStock: 950 },
  
  // Banjara Hills & Jubilee Hills (Affluent & High-Value Retail)
  { id: "STR-HYD-1011", name: "Banjara Hills Rd No 12 Exclusive Parlour", type: "exclusive", city: "Hyderabad", locality: "Banjara Hills", lat: 17.4156, lng: 78.4382, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Amul Parlours", skusCarried: 46, lastUpdate: "20 mins ago", stockRisk: "None", currentStock: 4100, targetStock: 4200 },
  { id: "STR-HYD-1012", name: "Jubilee Hills Rd No 36 Gourmet Hub", type: "modern_trade", city: "Hyderabad", locality: "Jubilee Hills", lat: 17.4325, lng: 78.4071, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Modern Trade", skusCarried: 62, lastUpdate: "1 hour ago", stockRisk: "Near-Expiry Risk", currentStock: 3900, targetStock: 4200 },
  { id: "STR-HYD-1013", name: "Taj Krishna Banqueting & Kitchens", type: "institutional", city: "Hyderabad", locality: "Banjara Hills", lat: 17.4182, lng: 78.4485, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Institutional / HoReCa", skusCarried: 28, lastUpdate: "5 hours ago", stockRisk: "None", currentStock: 3800, targetStock: 4000 },
  { id: "STR-HYD-1014", name: "Swiggy Instamart Banjara Pod", type: "quick_commerce", city: "Hyderabad", locality: "Banjara Hills", lat: 17.4121, lng: 78.4428, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Quick Commerce", skusCarried: 40, lastUpdate: "10 mins ago", stockRisk: "Critical Stockout Risk", currentStock: 510, targetStock: 2400 },
  { id: "STR-HYD-1015", name: "Filmnagar Balaji Kirana Stores", type: "general_trade", city: "Hyderabad", locality: "Jubilee Hills", lat: 17.4208, lng: 78.4055, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "General Trade", skusCarried: 20, lastUpdate: "3 hours ago", stockRisk: "None", currentStock: 1100, targetStock: 1200 },
  { id: "STR-HYD-1016", name: "Central Hyderabad Milk Booth #14", type: "exclusive", city: "Hyderabad", locality: "Panjagutta", lat: 17.4265, lng: 78.4518, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Amul Parlours", skusCarried: 26, lastUpdate: "25 mins ago", stockRisk: "None", currentStock: 2100, targetStock: 2200 },
  { id: "STR-HYD-1017", name: "Somajiguda City Center Supermarket", type: "modern_trade", city: "Hyderabad", locality: "Somajiguda", lat: 17.4215, lng: 78.4589, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Modern Trade", skusCarried: 52, lastUpdate: "50 mins ago", stockRisk: "None", currentStock: 4600, targetStock: 4800 },
  { id: "STR-HYD-1018", name: "NIMS Hospital Dietary Services", type: "institutional", city: "Hyderabad", locality: "Panjagutta", lat: 17.4228, lng: 78.4542, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Institutional / HoReCa", skusCarried: 16, lastUpdate: "6 hours ago", stockRisk: "None", currentStock: 1950, targetStock: 2000 },
  { id: "STR-HYD-1019", name: "Central Hyd Chilled Depot", type: "distributor", city: "Hyderabad", locality: "Sanath Nagar", lat: 17.4582, lng: 78.4419, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Distributor / Stockist", skusCarried: 120, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 42000, targetStock: 45000 },
  { id: "STR-HYD-1020", name: "Ameerpet Metro Station Parlour", type: "exclusive", city: "Hyderabad", locality: "Ameerpet", lat: 17.4374, lng: 78.4482, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Amul Parlours", skusCarried: 32, lastUpdate: "18 mins ago", stockRisk: "None", currentStock: 1980, targetStock: 2100 },

  // Kukatpally, Miyapur & Pragathi Nagar (Dense Residential Corridor)
  { id: "STR-HYD-1021", name: "Kukatpally KPHB Phase 1 Retail Outlet", type: "general_trade", city: "Hyderabad", locality: "Kukatpally", lat: 17.4932, lng: 78.3985, status: "active", distributorId: "DIST-HYD-NORTH", channel: "General Trade", skusCarried: 25, lastUpdate: "1 hour ago", stockRisk: "Critical Stockout Risk", currentStock: 280, targetStock: 1400 },
  { id: "STR-HYD-1022", name: "KPHB Main Road Amul Scooping Parlour", type: "exclusive", city: "Hyderabad", locality: "Kukatpally", lat: 17.4891, lng: 78.4012, status: "active", distributorId: "DIST-HYD-NORTH", channel: "Amul Parlours", skusCarried: 40, lastUpdate: "35 mins ago", stockRisk: "None", currentStock: 2900, targetStock: 3000 },
  { id: "STR-HYD-1023", name: "Spencer's Retail Kukatpally", type: "modern_trade", city: "Hyderabad", locality: "Kukatpally", lat: 17.4845, lng: 78.4112, status: "active", distributorId: "DIST-HYD-NORTH", channel: "Modern Trade", skusCarried: 56, lastUpdate: "1.5 hours ago", stockRisk: "None", currentStock: 4200, targetStock: 4500 },
  { id: "STR-HYD-1024", name: "Blinkit Dark Store KPHB Colony", type: "quick_commerce", city: "Hyderabad", locality: "Kukatpally", lat: 17.4988, lng: 78.3942, status: "active", distributorId: "DIST-HYD-NORTH", channel: "Quick Commerce", skusCarried: 36, lastUpdate: "8 mins ago", stockRisk: "Critical Stockout Risk", currentStock: 390, targetStock: 1800 },
  { id: "STR-HYD-1025", name: "Sri Sai Ram Milk & General Store", type: "general_trade", city: "Hyderabad", locality: "Pragathi Nagar", lat: 17.5124, lng: 78.3895, status: "active", distributorId: "DIST-HYD-NORTH", channel: "General Trade", skusCarried: 19, lastUpdate: "2.5 hours ago", stockRisk: "None", currentStock: 890, targetStock: 1000 },
  { id: "STR-HYD-1026", name: "Miyapur Metro Station Booth", type: "exclusive", city: "Hyderabad", locality: "Miyapur", lat: 17.4965, lng: 78.3614, status: "active", distributorId: "DIST-HYD-NORTH", channel: "Amul Parlours", skusCarried: 28, lastUpdate: "40 mins ago", stockRisk: "None", currentStock: 1850, targetStock: 2000 },
  { id: "STR-HYD-1027", name: "Allwyn Colony Sri Krishna Kirana", type: "general_trade", city: "Hyderabad", locality: "Miyapur", lat: 17.5021, lng: 78.3698, status: "active", distributorId: "DIST-HYD-NORTH", channel: "General Trade", skusCarried: 16, lastUpdate: "5 hours ago", stockRisk: "None", currentStock: 740, targetStock: 850 },
  { id: "STR-HYD-1028", name: "Chandanagar Super Bazaar", type: "modern_trade", city: "Hyderabad", locality: "Chandanagar", lat: 17.4925, lng: 78.3325, status: "active", distributorId: "DIST-HYD-NORTH", channel: "Modern Trade", skusCarried: 44, lastUpdate: "1 hour ago", stockRisk: "None", currentStock: 3100, targetStock: 3300 },
  { id: "STR-HYD-1029", name: "Nizampet Village Kirana Point", type: "general_trade", city: "Hyderabad", locality: "Nizampet", lat: 17.5195, lng: 78.3812, status: "inactive", distributorId: "DIST-HYD-NORTH", channel: "General Trade", skusCarried: 12, lastUpdate: "2 days ago", stockRisk: "Critical Stockout Risk", currentStock: 0, targetStock: 600 },
  { id: "STR-HYD-1030", name: "BHEL Township Staff Canteen", type: "institutional", city: "Hyderabad", locality: "Ramachandrapuram", lat: 17.5015, lng: 78.2912, status: "active", distributorId: "DIST-HYD-NORTH", channel: "Institutional / HoReCa", skusCarried: 22, lastUpdate: "4 hours ago", stockRisk: "None", currentStock: 2800, targetStock: 3000 },

  // Secunderabad, Begumpet & Trimulgherry (Cantonment & Northern Zone)
  { id: "STR-HYD-1031", name: "Secunderabad Railway Station Concourse Parlour", type: "exclusive", city: "Hyderabad", locality: "Secunderabad", lat: 17.4338, lng: 78.5012, status: "active", distributorId: "DIST-SEC-CENTRAL", channel: "Amul Parlours", skusCarried: 38, lastUpdate: "12 mins ago", stockRisk: "None", currentStock: 3200, targetStock: 3400 },
  { id: "STR-HYD-1032", name: "Clock Tower Heritage Milk Point", type: "exclusive", city: "Hyderabad", locality: "Secunderabad", lat: 17.4398, lng: 78.4985, status: "active", distributorId: "DIST-SEC-CENTRAL", channel: "Amul Parlours", skusCarried: 30, lastUpdate: "25 mins ago", stockRisk: "Critical Stockout Risk", currentStock: 380, targetStock: 1900 },
  { id: "STR-HYD-1033", name: "Trimulgherry Officers Mess Catering", type: "institutional", city: "Hyderabad", locality: "Trimulgherry", lat: 17.4725, lng: 78.5112, status: "active", distributorId: "DIST-SEC-CENTRAL", channel: "Institutional / HoReCa", skusCarried: 26, lastUpdate: "3 hours ago", stockRisk: "None", currentStock: 2400, targetStock: 2500 },
  { id: "STR-HYD-1034", name: "Karkhana Ratnadeep Supermarket", type: "modern_trade", city: "Hyderabad", locality: "Karkhana", lat: 17.4589, lng: 78.5025, status: "active", distributorId: "DIST-SEC-CENTRAL", channel: "Modern Trade", skusCarried: 50, lastUpdate: "50 mins ago", stockRisk: "None", currentStock: 4100, targetStock: 4300 },
  { id: "STR-HYD-1035", name: "Marredpally Neighborhood Grocery", type: "general_trade", city: "Hyderabad", locality: "West Marredpally", lat: 17.4485, lng: 78.5095, status: "active", distributorId: "DIST-SEC-CENTRAL", channel: "General Trade", skusCarried: 24, lastUpdate: "2 hours ago", stockRisk: "None", currentStock: 1150, targetStock: 1300 },
  { id: "STR-HYD-1036", name: "Begumpet Airport Plaza Parlour", type: "exclusive", city: "Hyderabad", locality: "Begumpet", lat: 17.4445, lng: 78.4682, status: "active", distributorId: "DIST-SEC-CENTRAL", channel: "Amul Parlours", skusCarried: 34, lastUpdate: "30 mins ago", stockRisk: "None", currentStock: 2600, targetStock: 2800 },
  { id: "STR-HYD-1037", name: "Balkampet Yellamma Kirana", type: "general_trade", city: "Hyderabad", locality: "Balkampet", lat: 17.4498, lng: 78.4525, status: "active", distributorId: "DIST-SEC-CENTRAL", channel: "General Trade", skusCarried: 17, lastUpdate: "4 hours ago", stockRisk: "None", currentStock: 820, targetStock: 900 },
  { id: "STR-HYD-1038", name: "Malkajgiri Anand Kirana Store", type: "general_trade", city: "Hyderabad", locality: "Malkajgiri", lat: 17.4512, lng: 78.5312, status: "active", distributorId: "DIST-SEC-EAST", channel: "General Trade", skusCarried: 21, lastUpdate: "3.5 hours ago", stockRisk: "Critical Stockout Risk", currentStock: 190, targetStock: 1100 },
  { id: "STR-HYD-1039", name: "Sainikpuri Zepto Fulfilment Hub", type: "quick_commerce", city: "Hyderabad", locality: "Sainikpuri", lat: 17.4895, lng: 78.5482, status: "active", distributorId: "DIST-SEC-EAST", channel: "Quick Commerce", skusCarried: 35, lastUpdate: "14 mins ago", stockRisk: "None", currentStock: 1900, targetStock: 2100 },
  { id: "STR-HYD-1040", name: "North Secunderabad Master Depot", type: "distributor", city: "Hyderabad", locality: "Bowenpally", lat: 17.4721, lng: 78.4812, status: "active", distributorId: "DIST-SEC-NORTH", channel: "Distributor / Stockist", skusCarried: 115, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 38000, targetStock: 40000 },

  // Uppal, LB Nagar, Dilsukhnagar & East Zone
  { id: "STR-HYD-1041", name: "Uppal Ring Road Amul Parlour", type: "exclusive", city: "Hyderabad", locality: "Uppal", lat: 17.4018, lng: 78.5598, status: "active", distributorId: "DIST-HYD-EAST", channel: "Amul Parlours", skusCarried: 36, lastUpdate: "22 mins ago", stockRisk: "None", currentStock: 2500, targetStock: 2600 },
  { id: "STR-HYD-1042", name: "Uppal Metro Station Food Kiosk", type: "exclusive", city: "Hyderabad", locality: "Uppal", lat: 17.3985, lng: 78.5562, status: "active", distributorId: "DIST-HYD-EAST", channel: "Amul Parlours", skusCarried: 24, lastUpdate: "45 mins ago", stockRisk: "None", currentStock: 1650, targetStock: 1800 },
  { id: "STR-HYD-1043", name: "East Hyderabad Main Milk Depot", type: "distributor", city: "Hyderabad", locality: "Uppal Industrial Area", lat: 17.4095, lng: 78.5682, status: "active", distributorId: "DIST-HYD-EAST", channel: "Distributor / Stockist", skusCarried: 125, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 48000, targetStock: 50000 },
  { id: "STR-HYD-1044", name: "Habsiguda More Supermarket", type: "modern_trade", city: "Hyderabad", locality: "Habsiguda", lat: 17.4128, lng: 78.5412, status: "active", distributorId: "DIST-HYD-EAST", channel: "Modern Trade", skusCarried: 46, lastUpdate: "1 hour ago", stockRisk: "None", currentStock: 3600, targetStock: 3800 },
  { id: "STR-HYD-1045", name: "CCMB Staff Cooperative Canteen", type: "institutional", city: "Hyderabad", locality: "Habsiguda", lat: 17.4185, lng: 78.5445, status: "active", distributorId: "DIST-HYD-EAST", channel: "Institutional / HoReCa", skusCarried: 20, lastUpdate: "4 hours ago", stockRisk: "None", currentStock: 1800, targetStock: 1900 },
  { id: "STR-HYD-1046", name: "LB Nagar Junction Quick Store", type: "quick_commerce", city: "Hyderabad", locality: "LB Nagar", lat: 17.3482, lng: 78.5521, status: "active", distributorId: "DIST-HYD-EAST", channel: "Quick Commerce", skusCarried: 32, lastUpdate: "11 mins ago", stockRisk: "Critical Stockout Risk", currentStock: 290, targetStock: 1700 },
  { id: "STR-HYD-1047", name: "Dilsukhnagar Main Rd Amul Booth", type: "exclusive", city: "Hyderabad", locality: "Dilsukhnagar", lat: 17.3689, lng: 78.5285, status: "active", distributorId: "DIST-HYD-EAST", channel: "Amul Parlours", skusCarried: 34, lastUpdate: "18 mins ago", stockRisk: "None", currentStock: 2400, targetStock: 2500 },
  { id: "STR-HYD-1048", name: "Kothapet Fruit Market Dairy Point", type: "general_trade", city: "Hyderabad", locality: "Kothapet", lat: 17.3621, lng: 78.5418, status: "active", distributorId: "DIST-HYD-EAST", channel: "General Trade", skusCarried: 22, lastUpdate: "3 hours ago", stockRisk: "None", currentStock: 1200, targetStock: 1300 },
  { id: "STR-HYD-1049", name: "Nagole Metro Station Retailer", type: "general_trade", city: "Hyderabad", locality: "Nagole", lat: 17.3785, lng: 78.5612, status: "active", distributorId: "DIST-HYD-EAST", channel: "General Trade", skusCarried: 18, lastUpdate: "2 hours ago", stockRisk: "None", currentStock: 950, targetStock: 1050 },
  { id: "STR-HYD-1050", name: "Vanasthalipuram Sri Balaji Kirana", type: "general_trade", city: "Hyderabad", locality: "Vanasthalipuram", lat: 17.3325, lng: 78.5712, status: "active", distributorId: "DIST-HYD-EAST", channel: "General Trade", skusCarried: 19, lastUpdate: "5 hours ago", stockRisk: "None", currentStock: 870, targetStock: 950 },

  // Old City, Charminar & South Zone
  { id: "STR-HYD-1051", name: "Charminar Monument Heritage Booth", type: "exclusive", city: "Hyderabad", locality: "Charminar", lat: 17.3616, lng: 78.4747, status: "active", distributorId: "DIST-HYD-SOUTH", channel: "Amul Parlours", skusCarried: 28, lastUpdate: "30 mins ago", stockRisk: "None", currentStock: 2100, targetStock: 2200 },
  { id: "STR-HYD-1052", name: "Lad Bazaar Traditional Milk Point", type: "general_trade", city: "Hyderabad", locality: "Charminar", lat: 17.3625, lng: 78.4712, status: "active", distributorId: "DIST-HYD-SOUTH", channel: "General Trade", skusCarried: 15, lastUpdate: "4 hours ago", stockRisk: "None", currentStock: 780, targetStock: 850 },
  { id: "STR-HYD-1053", name: "Shadab Hotel Bulk Dairy Supplies", type: "institutional", city: "Hyderabad", locality: "Madina", lat: 17.3685, lng: 78.4762, status: "active", distributorId: "DIST-HYD-SOUTH", channel: "Institutional / HoReCa", skusCarried: 18, lastUpdate: "2 hours ago", stockRisk: "None", currentStock: 3200, targetStock: 3300 },
  { id: "STR-HYD-1054", name: "Bahadurpura Zoo Park Amul Kiosk", type: "exclusive", city: "Hyderabad", locality: "Bahadurpura", lat: 17.3512, lng: 78.4518, status: "active", distributorId: "DIST-HYD-SOUTH", channel: "Amul Parlours", skusCarried: 22, lastUpdate: "1 hour ago", stockRisk: "None", currentStock: 1400, targetStock: 1500 },
  { id: "STR-HYD-1055", name: "Falaknuma Royal Dairy Provisions", type: "general_trade", city: "Hyderabad", locality: "Falaknuma", lat: 17.3312, lng: 78.4682, status: "active", distributorId: "DIST-HYD-SOUTH", channel: "General Trade", skusCarried: 17, lastUpdate: "3 hours ago", stockRisk: "Critical Stockout Risk", currentStock: 180, targetStock: 850 },
  { id: "STR-HYD-1056", name: "Chandrayangutta Kirana Bazaar", type: "general_trade", city: "Hyderabad", locality: "Chandrayangutta", lat: 17.3218, lng: 78.4812, status: "active", distributorId: "DIST-HYD-SOUTH", channel: "General Trade", skusCarried: 14, lastUpdate: "5 hours ago", stockRisk: "None", currentStock: 690, targetStock: 750 },
  { id: "STR-HYD-1057", name: "Santosh Nagar Balaji Supermarket", type: "modern_trade", city: "Hyderabad", locality: "Santosh Nagar", lat: 17.3518, lng: 78.5085, status: "active", distributorId: "DIST-HYD-SOUTH", channel: "Modern Trade", skusCarried: 38, lastUpdate: "1.5 hours ago", stockRisk: "None", currentStock: 2800, targetStock: 3000 },
  { id: "STR-HYD-1058", name: "Malakpet Super Bazaar", type: "modern_trade", city: "Hyderabad", locality: "Malakpet", lat: 17.3712, lng: 78.4985, status: "active", distributorId: "DIST-HYD-SOUTH", channel: "Modern Trade", skusCarried: 42, lastUpdate: "1 hour ago", stockRisk: "None", currentStock: 3200, targetStock: 3400 },
  { id: "STR-HYD-1059", name: "South Hyderabad Cold Hub", type: "distributor", city: "Hyderabad", locality: "Falaknuma", lat: 17.3285, lng: 78.4612, status: "active", distributorId: "DIST-HYD-SOUTH", channel: "Distributor / Stockist", skusCarried: 98, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 29000, targetStock: 31000 },
  { id: "STR-HYD-1060", name: "Mehdipatnam Bus Terminal Parlour", type: "exclusive", city: "Hyderabad", locality: "Mehdipatnam", lat: 17.3912, lng: 78.4418, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Amul Parlours", skusCarried: 32, lastUpdate: "20 mins ago", stockRisk: "None", currentStock: 2400, targetStock: 2500 },

  // Central Core: Abids, Nampally, Himayatnagar & Narayanaguda
  { id: "STR-HYD-1061", name: "Abids GPO Heritage Amul Kiosk", type: "exclusive", city: "Hyderabad", locality: "Abids", lat: 17.3925, lng: 78.4765, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Amul Parlours", skusCarried: 34, lastUpdate: "15 mins ago", stockRisk: "None", currentStock: 2550, targetStock: 2700 },
  { id: "STR-HYD-1062", name: "Himayatnagar Modern Provisions", type: "general_trade", city: "Hyderabad", locality: "Himayatnagar", lat: 17.4021, lng: 78.4885, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "General Trade", skusCarried: 24, lastUpdate: "2 hours ago", stockRisk: "None", currentStock: 1300, targetStock: 1400 },
  { id: "STR-HYD-1063", name: "Narayanaguda Flyover Milk Booth", type: "exclusive", city: "Hyderabad", locality: "Narayanaguda", lat: 17.3985, lng: 78.4912, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Amul Parlours", skusCarried: 28, lastUpdate: "35 mins ago", stockRisk: "Critical Stockout Risk", currentStock: 320, targetStock: 1800 },
  { id: "STR-HYD-1064", name: "Nampally Station Road Kirana", type: "general_trade", city: "Hyderabad", locality: "Nampally", lat: 17.3885, lng: 78.4682, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "General Trade", skusCarried: 16, lastUpdate: "4 hours ago", stockRisk: "None", currentStock: 820, targetStock: 900 },
  { id: "STR-HYD-1065", name: "Basheerbagh Babukhan Estate Parlour", type: "exclusive", city: "Hyderabad", locality: "Basheerbagh", lat: 17.4012, lng: 78.4745, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Amul Parlours", skusCarried: 36, lastUpdate: "10 mins ago", stockRisk: "None", currentStock: 2900, targetStock: 3000 },
  { id: "STR-HYD-1066", name: "Banjara Hills Swiggy Pod 2", type: "quick_commerce", city: "Hyderabad", locality: "Banjara Hills", lat: 17.4245, lng: 78.4312, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Quick Commerce", skusCarried: 38, lastUpdate: "12 mins ago", stockRisk: "None", currentStock: 2100, targetStock: 2300 },
  { id: "STR-HYD-1067", name: "Khairatabad Anand Dahi Point", type: "general_trade", city: "Hyderabad", locality: "Khairatabad", lat: 17.4112, lng: 78.4612, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "General Trade", skusCarried: 18, lastUpdate: "3 hours ago", stockRisk: "None", currentStock: 910, targetStock: 1000 },
  { id: "STR-HYD-1068", name: "Secretariat Staff Canteen", type: "institutional", city: "Hyderabad", locality: "Khairatabad", lat: 17.4085, lng: 78.4695, status: "active", distributorId: "DIST-HYD-CENTRAL", channel: "Institutional / HoReCa", skusCarried: 22, lastUpdate: "5 hours ago", stockRisk: "None", currentStock: 2400, targetStock: 2500 },
  { id: "STR-HYD-1069", name: "Moosapet Metro Wholesale Depot", type: "distributor", city: "Hyderabad", locality: "Moosapet", lat: 17.4695, lng: 78.4285, status: "active", distributorId: "DIST-HYD-WEST", channel: "Distributor / Stockist", skusCarried: 112, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 36000, targetStock: 38000 },
  { id: "STR-HYD-1070", name: "Balanagar Industrial Canteen Supplies", type: "institutional", city: "Hyderabad", locality: "Balanagar", lat: 17.4785, lng: 78.4412, status: "active", distributorId: "DIST-HYD-NORTH", channel: "Institutional / HoReCa", skusCarried: 20, lastUpdate: "6 hours ago", stockRisk: "None", currentStock: 2100, targetStock: 2200 },

  // --- TELANGANA TIER-2 REGIONAL HUBS (25 Outlets) ---
  // Warangal / Hanamkonda (Tri-Cities Hub)
  { id: "STR-WGL-2001", name: "Warangal Kazipet Junction Parlour", type: "exclusive", city: "Warangal", locality: "Kazipet", lat: 17.9785, lng: 79.5285, status: "active", distributorId: "DIST-WGL-HUB", channel: "Amul Parlours", skusCarried: 36, lastUpdate: "35 mins ago", stockRisk: "None", currentStock: 2800, targetStock: 2900 },
  { id: "STR-WGL-2002", name: "Hanamkonda Main Road Milk Booth", type: "exclusive", city: "Warangal", locality: "Hanamkonda", lat: 18.0125, lng: 79.5512, status: "active", distributorId: "DIST-WGL-HUB", channel: "Amul Parlours", skusCarried: 30, lastUpdate: "40 mins ago", stockRisk: "Critical Stockout Risk", currentStock: 340, targetStock: 1950 },
  { id: "STR-WGL-2003", name: "Warangal Regional Master Stockist", type: "distributor", city: "Warangal", locality: "Industrial Estate", lat: 17.9895, lng: 79.5812, status: "active", distributorId: "DIST-WGL-HUB", channel: "Distributor / Stockist", skusCarried: 95, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 28000, targetStock: 30000 },
  { id: "STR-WGL-2004", name: "NIT Warangal Campus Canteen", type: "institutional", city: "Warangal", locality: "Kazipet", lat: 17.9835, lng: 79.5312, status: "active", distributorId: "DIST-WGL-HUB", channel: "Institutional / HoReCa", skusCarried: 24, lastUpdate: "3 hours ago", stockRisk: "None", currentStock: 2300, targetStock: 2400 },
  { id: "STR-WGL-2005", name: "Balaji Kirana Hanamkonda Chowrasta", type: "general_trade", city: "Warangal", locality: "Hanamkonda", lat: 18.0055, lng: 79.5625, status: "active", distributorId: "DIST-WGL-HUB", channel: "General Trade", skusCarried: 18, lastUpdate: "2 hours ago", stockRisk: "None", currentStock: 920, targetStock: 1000 },
  { id: "STR-WGL-2006", name: "Warangal Reliance Smart Superstore", type: "modern_trade", city: "Warangal", locality: "Subedari", lat: 18.0012, lng: 79.5425, status: "active", distributorId: "DIST-WGL-HUB", channel: "Modern Trade", skusCarried: 44, lastUpdate: "1 hour ago", stockRisk: "None", currentStock: 3200, targetStock: 3400 },
  { id: "STR-WGL-2007", name: "Kakatiya Medical College Hostel", type: "institutional", city: "Warangal", locality: "Warangal City", lat: 17.9912, lng: 79.5985, status: "active", distributorId: "DIST-WGL-HUB", channel: "Institutional / HoReCa", skusCarried: 19, lastUpdate: "5 hours ago", stockRisk: "None", currentStock: 1800, targetStock: 1900 },

  // Karimnagar (North Telangana Agro-Industrial Belt)
  { id: "STR-KMR-2008", name: "Karimnagar Tower Circle Parlour", type: "exclusive", city: "Karimnagar", locality: "Clock Tower", lat: 18.4385, lng: 79.1285, status: "active", distributorId: "DIST-KMR-HUB", channel: "Amul Parlours", skusCarried: 34, lastUpdate: "28 mins ago", stockRisk: "None", currentStock: 2500, targetStock: 2600 },
  { id: "STR-KMR-2009", name: "Karimnagar District Stockist Depot", type: "distributor", city: "Karimnagar", locality: "Kothirampur", lat: 18.4295, lng: 79.1398, status: "active", distributorId: "DIST-KMR-HUB", channel: "Distributor / Stockist", skusCarried: 88, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 22000, targetStock: 24000 },
  { id: "STR-KMR-2010", name: "Sri Venkateshwara Kirana Stores", type: "general_trade", city: "Karimnagar", locality: "Mukarampura", lat: 18.4412, lng: 79.1195, status: "active", distributorId: "DIST-KMR-HUB", channel: "General Trade", skusCarried: 16, lastUpdate: "3.5 hours ago", stockRisk: "Critical Stockout Risk", currentStock: 150, targetStock: 800 },
  { id: "STR-KMR-2011", name: "Karimnagar D-Mart Supermarket", type: "modern_trade", city: "Karimnagar", locality: "Collectorate Road", lat: 18.4215, lng: 79.1482, status: "active", distributorId: "DIST-KMR-HUB", channel: "Modern Trade", skusCarried: 40, lastUpdate: "1.5 hours ago", stockRisk: "None", currentStock: 2900, targetStock: 3100 },
  { id: "STR-KMR-2012", name: "Manair Hotel Catering & Events", type: "institutional", city: "Karimnagar", locality: "Mankammathota", lat: 18.4325, lng: 79.1255, status: "active", distributorId: "DIST-KMR-HUB", channel: "Institutional / HoReCa", skusCarried: 18, lastUpdate: "4 hours ago", stockRisk: "None", currentStock: 1750, targetStock: 1850 },

  // Nizamabad (North-West Border Zone)
  { id: "STR-NZB-2013", name: "Nizamabad Railway Feeder Booth", type: "exclusive", city: "Nizamabad", locality: "Railway Station Road", lat: 18.6725, lng: 78.0985, status: "active", distributorId: "DIST-NZB-HUB", channel: "Amul Parlours", skusCarried: 30, lastUpdate: "35 mins ago", stockRisk: "None", currentStock: 2200, targetStock: 2300 },
  { id: "STR-NZB-2014", name: "Nizamabad District Dairy Depot", type: "distributor", city: "Nizamabad", locality: "Khaleelwadi", lat: 18.6795, lng: 78.1095, status: "active", distributorId: "DIST-NZB-HUB", channel: "Distributor / Stockist", skusCarried: 82, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 19500, targetStock: 21000 },
  { id: "STR-NZB-2015", name: "Goutham Kirana Provisions", type: "general_trade", city: "Nizamabad", locality: "Subhash Nagar", lat: 18.6655, lng: 78.0895, status: "active", distributorId: "DIST-NZB-HUB", channel: "General Trade", skusCarried: 15, lastUpdate: "4 hours ago", stockRisk: "None", currentStock: 680, targetStock: 750 },
  { id: "STR-NZB-2016", name: "Nizamabad Medical College Hospital", type: "institutional", city: "Nizamabad", locality: "Khaleelwadi", lat: 18.6812, lng: 78.1145, status: "active", distributorId: "DIST-NZB-HUB", channel: "Institutional / HoReCa", skusCarried: 16, lastUpdate: "6 hours ago", stockRisk: "None", currentStock: 1500, targetStock: 1600 },

  // Khammam (Eastern Coal & Granites Hub)
  { id: "STR-KHM-2017", name: "Khammam Bus Stand Parlour", type: "exclusive", city: "Khammam", locality: "RTC Bus Station", lat: 17.2475, lng: 80.1512, status: "active", distributorId: "DIST-KHM-HUB", channel: "Amul Parlours", skusCarried: 32, lastUpdate: "25 mins ago", stockRisk: "Critical Stockout Risk", currentStock: 310, targetStock: 1850 },
  { id: "STR-KHM-2018", name: "Khammam District Stockist", type: "distributor", city: "Khammam", locality: "Mamillagudem", lat: 17.2585, lng: 80.1625, status: "active", distributorId: "DIST-KHM-HUB", channel: "Distributor / Stockist", skusCarried: 85, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 21000, targetStock: 22500 },
  { id: "STR-KHM-2019", name: "Srinivasa Kirana Store", type: "general_trade", city: "Khammam", locality: "Wyra Road", lat: 17.2412, lng: 80.1425, status: "active", distributorId: "DIST-KHM-HUB", channel: "General Trade", skusCarried: 17, lastUpdate: "3 hours ago", stockRisk: "None", currentStock: 820, targetStock: 900 },
  { id: "STR-KHM-2020", name: "Khammam More Supermarket", type: "modern_trade", city: "Khammam", locality: "Mayuri Centre", lat: 17.2512, lng: 80.1585, status: "active", distributorId: "DIST-KHM-HUB", channel: "Modern Trade", skusCarried: 38, lastUpdate: "2 hours ago", stockRisk: "None", currentStock: 2600, targetStock: 2800 },

  // Mahbubnagar (South Telangana Gateway)
  { id: "STR-MBN-2021", name: "Mahbubnagar Station Rd Parlour", type: "exclusive", city: "Mahbubnagar", locality: "Station Road", lat: 16.7455, lng: 77.9985, status: "active", distributorId: "DIST-MBN-HUB", channel: "Amul Parlours", skusCarried: 28, lastUpdate: "45 mins ago", stockRisk: "None", currentStock: 1950, targetStock: 2100 },
  { id: "STR-MBN-2022", name: "Mahbubnagar Cold Stockist", type: "distributor", city: "Mahbubnagar", locality: "Boyapally", lat: 16.7385, lng: 78.0112, status: "active", distributorId: "DIST-MBN-HUB", channel: "Distributor / Stockist", skusCarried: 78, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 17500, targetStock: 19000 },
  { id: "STR-MBN-2023", name: "Sri Sai Baba Kirana", type: "general_trade", city: "Mahbubnagar", locality: "One Town", lat: 16.7495, lng: 77.9895, status: "active", distributorId: "DIST-MBN-HUB", channel: "General Trade", skusCarried: 14, lastUpdate: "5 hours ago", stockRisk: "None", currentStock: 640, targetStock: 700 },
  { id: "STR-MBN-2024", name: "Jadcherla Highway Parlour", type: "exclusive", city: "Mahbubnagar", locality: "Jadcherla", lat: 16.7712, lng: 78.1412, status: "active", distributorId: "DIST-MBN-HUB", channel: "Amul Parlours", skusCarried: 26, lastUpdate: "1 hour ago", stockRisk: "None", currentStock: 1650, targetStock: 1800 },
  { id: "STR-MBN-2025", name: "Palamuru University Canteen", type: "institutional", city: "Mahbubnagar", locality: "University Campus", lat: 16.7215, lng: 78.0312, status: "inactive", distributorId: "DIST-MBN-HUB", channel: "Institutional / HoReCa", skusCarried: 12, lastUpdate: "3 days ago", stockRisk: "Critical Stockout Risk", currentStock: 0, targetStock: 900 },

  // --- ANDHRA PRADESH COASTAL & RAYALASEEMA (33 Outlets) ---
  // Vijayawada & Amaravati Capital Region (Commercial Heartland)
  { id: "STR-BZA-3001", name: "Vijayawada Benz Circle Flagship Parlour", type: "exclusive", city: "Vijayawada", locality: "Benz Circle", lat: 16.4985, lng: 80.6512, status: "active", distributorId: "DIST-BZA-HUB", channel: "Amul Parlours", skusCarried: 44, lastUpdate: "15 mins ago", stockRisk: "None", currentStock: 3800, targetStock: 4000 },
  { id: "STR-BZA-3002", name: "BZA Railway Station Terminal Parlour", type: "exclusive", city: "Vijayawada", locality: "Railway Station", lat: 16.5185, lng: 80.6212, status: "active", distributorId: "DIST-BZA-HUB", channel: "Amul Parlours", skusCarried: 38, lastUpdate: "20 mins ago", stockRisk: "Critical Stockout Risk", currentStock: 410, targetStock: 2200 },
  { id: "STR-BZA-3003", name: "Vijayawada Central Distribution Hub", type: "distributor", city: "Vijayawada", locality: "Auto Nagar", lat: 16.4912, lng: 80.6812, status: "active", distributorId: "DIST-BZA-HUB", channel: "Distributor / Stockist", skusCarried: 130, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 52000, targetStock: 55000 },
  { id: "STR-BZA-3004", name: "Blinkit Dark Store Benz Circle", type: "quick_commerce", city: "Vijayawada", locality: "Benz Circle", lat: 16.5021, lng: 80.6485, status: "active", distributorId: "DIST-BZA-HUB", channel: "Quick Commerce", skusCarried: 36, lastUpdate: "10 mins ago", stockRisk: "None", currentStock: 1950, targetStock: 2100 },
  { id: "STR-BZA-3005", name: "Ratnadeep Supermarket MG Road", type: "modern_trade", city: "Vijayawada", locality: "MG Road", lat: 16.5085, lng: 80.6385, status: "active", distributorId: "DIST-BZA-HUB", channel: "Modern Trade", skusCarried: 52, lastUpdate: "45 mins ago", stockRisk: "None", currentStock: 4200, targetStock: 4400 },
  { id: "STR-BZA-3006", name: "Governorpet Sri Lakshmi Kirana", type: "general_trade", city: "Vijayawada", locality: "Governorpet", lat: 16.5125, lng: 80.6312, status: "active", distributorId: "DIST-BZA-HUB", channel: "General Trade", skusCarried: 20, lastUpdate: "3 hours ago", stockRisk: "None", currentStock: 1100, targetStock: 1200 },
  { id: "STR-BZA-3007", name: "AIIMS Mangalagiri Dietary Services", type: "institutional", city: "Vijayawada", locality: "Mangalagiri", lat: 16.4385, lng: 80.5612, status: "active", distributorId: "DIST-BZA-HUB", channel: "Institutional / HoReCa", skusCarried: 24, lastUpdate: "4 hours ago", stockRisk: "None", currentStock: 3100, targetStock: 3300 },
  { id: "STR-BZA-3008", name: "One Town Kaleswara Rao Market Booth", type: "general_trade", city: "Vijayawada", locality: "One Town", lat: 16.5212, lng: 80.6125, status: "active", distributorId: "DIST-BZA-HUB", channel: "General Trade", skusCarried: 18, lastUpdate: "2.5 hours ago", stockRisk: "None", currentStock: 940, targetStock: 1050 },

  // Guntur (Agricultural & Tobacco Trade Capital)
  { id: "STR-GNT-3009", name: "Guntur Lakshmipuram Parlour", type: "exclusive", city: "Guntur", locality: "Lakshmipuram", lat: 16.2985, lng: 80.4412, status: "active", distributorId: "DIST-GNT-HUB", channel: "Amul Parlours", skusCarried: 34, lastUpdate: "30 mins ago", stockRisk: "None", currentStock: 2600, targetStock: 2700 },
  { id: "STR-GNT-3010", name: "Guntur Regional Stockist Depot", type: "distributor", city: "Guntur", locality: "Autonagar", lat: 16.3125, lng: 80.4612, status: "active", distributorId: "DIST-GNT-HUB", channel: "Distributor / Stockist", skusCarried: 90, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 25000, targetStock: 27000 },
  { id: "STR-GNT-3011", name: "Arundelpet Balaji Kirana Store", type: "general_trade", city: "Guntur", locality: "Arundelpet", lat: 16.3055, lng: 80.4325, status: "active", distributorId: "DIST-GNT-HUB", channel: "General Trade", skusCarried: 19, lastUpdate: "4 hours ago", stockRisk: "Critical Stockout Risk", currentStock: 210, targetStock: 1000 },
  { id: "STR-GNT-3012", name: "Guntur D-Mart Retail", type: "modern_trade", city: "Guntur", locality: "Stambalagaruvu", lat: 16.2895, lng: 80.4285, status: "active", distributorId: "DIST-GNT-HUB", channel: "Modern Trade", skusCarried: 46, lastUpdate: "1 hour ago", stockRisk: "None", currentStock: 3400, targetStock: 3600 },
  { id: "STR-GNT-3013", name: "Guntur Medical College Hospital", type: "institutional", city: "Guntur", locality: "Kothapet", lat: 16.3012, lng: 80.4512, status: "active", distributorId: "DIST-GNT-HUB", channel: "Institutional / HoReCa", skusCarried: 20, lastUpdate: "5 hours ago", stockRisk: "None", currentStock: 2100, targetStock: 2200 },

  // Visakhapatnam (Coastal Metro & Industrial Port City)
  { id: "STR-VTZ-3014", name: "Vizag Siripuram Junction Exclusive", type: "exclusive", city: "Visakhapatnam", locality: "Siripuram", lat: 17.7215, lng: 83.3185, status: "active", distributorId: "DIST-VTZ-HUB", channel: "Amul Parlours", skusCarried: 42, lastUpdate: "18 mins ago", stockRisk: "None", currentStock: 3600, targetStock: 3800 },
  { id: "STR-VTZ-3015", name: "RK Beach Promenade Amul Scooping", type: "exclusive", city: "Visakhapatnam", locality: "Beach Road", lat: 17.7145, lng: 83.3245, status: "active", distributorId: "DIST-VTZ-HUB", channel: "Amul Parlours", skusCarried: 36, lastUpdate: "25 mins ago", stockRisk: "None", currentStock: 2900, targetStock: 3100 },
  { id: "STR-VTZ-3016", name: "Vizag North Autonagar Depot", type: "distributor", city: "Visakhapatnam", locality: "Gajuwaka Industrial", lat: 17.6895, lng: 83.2185, status: "active", distributorId: "DIST-VTZ-HUB", channel: "Distributor / Stockist", skusCarried: 118, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 44000, targetStock: 46000 },
  { id: "STR-VTZ-3017", name: "Swiggy Instamart MVP Colony Hub", type: "quick_commerce", city: "Visakhapatnam", locality: "MVP Colony", lat: 17.7385, lng: 83.3395, status: "active", distributorId: "DIST-VTZ-HUB", channel: "Quick Commerce", skusCarried: 38, lastUpdate: "8 mins ago", stockRisk: "Critical Stockout Risk", currentStock: 410, targetStock: 2200 },
  { id: "STR-VTZ-3018", name: "Spencer's Hypermarket Vizag Central", type: "modern_trade", city: "Visakhapatnam", locality: "Dwaraka Nagar", lat: 17.7285, lng: 83.3095, status: "active", distributorId: "DIST-VTZ-HUB", channel: "Modern Trade", skusCarried: 54, lastUpdate: "50 mins ago", stockRisk: "None", currentStock: 4600, targetStock: 4800 },
  { id: "STR-VTZ-3019", name: "Gajuwaka Steel Plant Gate Kirana", type: "general_trade", city: "Visakhapatnam", locality: "Gajuwaka", lat: 17.6912, lng: 83.2085, status: "active", distributorId: "DIST-VTZ-HUB", channel: "General Trade", skusCarried: 22, lastUpdate: "3 hours ago", stockRisk: "None", currentStock: 1150, targetStock: 1250 },
  { id: "STR-VTZ-3020", name: "Eastern Naval Command Canteen", type: "institutional", city: "Visakhapatnam", locality: "Naval Base", lat: 17.7012, lng: 83.2785, status: "active", distributorId: "DIST-VTZ-HUB", channel: "Institutional / HoReCa", skusCarried: 30, lastUpdate: "4 hours ago", stockRisk: "None", currentStock: 4100, targetStock: 4300 },
  { id: "STR-VTZ-3021", name: "Rushikonda IT SEZ Kiosk", type: "exclusive", city: "Visakhapatnam", locality: "Rushikonda", lat: 17.7812, lng: 83.3812, status: "active", distributorId: "DIST-VTZ-HUB", channel: "Amul Parlours", skusCarried: 26, lastUpdate: "1 hour ago", stockRisk: "None", currentStock: 1800, targetStock: 1950 },
  { id: "STR-VTZ-3022", name: "Dabagardens City Center Provisions", type: "general_trade", city: "Visakhapatnam", locality: "Dabagardens", lat: 17.7125, lng: 83.2985, status: "active", distributorId: "DIST-VTZ-HUB", channel: "General Trade", skusCarried: 20, lastUpdate: "2.5 hours ago", stockRisk: "Near-Expiry Risk", currentStock: 980, targetStock: 1100 },

  // Rajahmundry & Kakinada (Godavari Agro-Belt)
  { id: "STR-RJY-3023", name: "Rajahmundry Pushkar Ghat Parlour", type: "exclusive", city: "Rajahmundry", locality: "Ghat Road", lat: 17.0012, lng: 81.7785, status: "active", distributorId: "DIST-RJY-HUB", channel: "Amul Parlours", skusCarried: 32, lastUpdate: "35 mins ago", stockRisk: "None", currentStock: 2400, targetStock: 2500 },
  { id: "STR-RJY-3024", name: "Rajahmundry Godavari Stockist", type: "distributor", city: "Rajahmundry", locality: "Danavaipeta", lat: 17.0095, lng: 81.7895, status: "active", distributorId: "DIST-RJY-HUB", channel: "Distributor / Stockist", skusCarried: 84, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 20500, targetStock: 22000 },
  { id: "STR-RJY-3025", name: "Kakinada Port Town Dairy Outlet", type: "exclusive", city: "Kakinada", locality: "Main Road", lat: 16.9612, lng: 82.2385, status: "active", distributorId: "DIST-RJY-HUB", channel: "Amul Parlours", skusCarried: 30, lastUpdate: "45 mins ago", stockRisk: "None", currentStock: 2150, targetStock: 2300 },
  { id: "STR-RJY-3026", name: "Kakinada Bhanugudi Kirana", type: "general_trade", city: "Kakinada", locality: "Bhanugudi", lat: 16.9725, lng: 82.2485, status: "active", distributorId: "DIST-RJY-HUB", channel: "General Trade", skusCarried: 17, lastUpdate: "4 hours ago", stockRisk: "Critical Stockout Risk", currentStock: 160, targetStock: 850 },

  // Tirupati (Pilgrimage & Institutional Mega Hub)
  { id: "STR-TPT-3027", name: "Tirupati Central Bus Station Parlour", type: "exclusive", city: "Tirupati", locality: "RTC Complex", lat: 13.6285, lng: 79.4185, status: "active", distributorId: "DIST-TPT-HUB", channel: "Amul Parlours", skusCarried: 38, lastUpdate: "20 mins ago", stockRisk: "None", currentStock: 3100, targetStock: 3300 },
  { id: "STR-TPT-3028", name: "Tirupati Pilgrimage Redistribution Hub", type: "distributor", city: "Tirupati", locality: "Renigunta Road", lat: 13.6395, lng: 79.4485, status: "active", distributorId: "DIST-TPT-HUB", channel: "Distributor / Stockist", skusCarried: 92, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 29000, targetStock: 31000 },
  { id: "STR-TPT-3029", name: "TTD Pilgrim Canteens Bulk Supply", type: "institutional", city: "Tirupati", locality: "Alipiri", lat: 13.6512, lng: 79.3985, status: "active", distributorId: "DIST-TPT-HUB", channel: "Institutional / HoReCa", skusCarried: 22, lastUpdate: "2 hours ago", stockRisk: "None", currentStock: 4800, targetStock: 5000 },
  { id: "STR-TPT-3030", name: "Bhavani Nagar Balaji Kirana", type: "general_trade", city: "Tirupati", locality: "Bhavani Nagar", lat: 13.6215, lng: 79.4285, status: "active", distributorId: "DIST-TPT-HUB", channel: "General Trade", skusCarried: 18, lastUpdate: "3 hours ago", stockRisk: "None", currentStock: 950, targetStock: 1050 },

  // Nellore & Southern Coastal Zone
  { id: "STR-NLR-3031", name: "Nellore Trunk Road Flagship Parlour", type: "exclusive", city: "Nellore", locality: "Trunk Road", lat: 14.4425, lng: 79.9885, status: "active", distributorId: "DIST-NLR-HUB", channel: "Amul Parlours", skusCarried: 34, lastUpdate: "40 mins ago", stockRisk: "None", currentStock: 2500, targetStock: 2650 },
  { id: "STR-NLR-3032", name: "Nellore District Cold Depot", type: "distributor", city: "Nellore", locality: "Autonagar", lat: 14.4585, lng: 79.9995, status: "active", distributorId: "DIST-NLR-HUB", channel: "Distributor / Stockist", skusCarried: 80, lastUpdate: "Live Sync", stockRisk: "None", currentStock: 18500, targetStock: 20000 },
  { id: "STR-NLR-3033", name: "Nellore Gandhi Nagar Kirana", type: "general_trade", city: "Nellore", locality: "Gandhi Nagar", lat: 14.4385, lng: 79.9795, status: "active", distributorId: "DIST-NLR-HUB", channel: "General Trade", skusCarried: 16, lastUpdate: "4 hours ago", stockRisk: "Critical Stockout Risk", currentStock: 170, targetStock: 800 }
];

// 12-Week Rolling Demand Time Series with Festival / Event Annotations
const TIMEFRAME_WEEKS = [
  { label: "Jan 12", date: "2026-01-12", isPast: true },
  { label: "Jan 19", date: "2026-01-19", isPast: true },
  { label: "Jan 26", date: "2026-01-26", isPast: true, event: "Republic Day Holiday" },
  { label: "Feb 02", date: "2026-02-02", isPast: true },
  { label: "Feb 09", date: "2026-02-09", isPast: false, isToday: true }, // Today indicator
  { label: "Feb 16", date: "2026-02-16", isPast: false },
  { label: "Feb 23", date: "2026-02-23", isPast: false, promo: "Ramadan Surge" },
  { label: "Mar 02", date: "2026-03-02", isPast: false, promo: "Ramadan Surge" },
  { label: "Mar 09", date: "2026-03-09", isPast: false, promo: "Ramadan Surge" },
  { label: "Mar 16", date: "2026-03-16", isPast: false, promo: "Ramadan / Ugadi" },
  { label: "Mar 23", date: "2026-03-23", isPast: false },
  { label: "Mar 30", date: "2026-03-30", isPast: false },
  { label: "Apr 06", date: "2026-04-06", isPast: false },
  { label: "Apr 13", date: "2026-04-13", isPast: false },
  { label: "Apr 20", date: "2026-04-20", isPast: false, promo: "Summer Heatwave" },
  { label: "Apr 27", date: "2026-04-27", isPast: false, promo: "Summer Heatwave" },
  { label: "May 04", date: "2026-05-04", isPast: false, promo: "Summer Heatwave" }
];

// SKU Time-Series Data Generator (Deterministic & Plausible for Amul Portfolio)
function getSkuTimeSeries(skuId) {
  const sku = AMUL_SKUS.find(s => s.sku_id === skuId) || AMUL_SKUS[0];
  const base = sku.forecast_units / 4.0; // weekly scale
  
  // Historical sales (first 5 points up to Feb 9)
  const historical = [
    Math.round(base * 0.94),
    Math.round(base * 0.96),
    Math.round(base * 1.02), // Rep Day boost
    Math.round(base * 0.97),
    Math.round(base * 0.99)
  ];
  
  // Future forecast baseline (from Feb 9 onward)
  const baseline = [
    Math.round(base * 0.99),
    Math.round(base * 1.01),
    Math.round(base * 1.04),
    Math.round(base * 1.07),
    Math.round(base * 1.09),
    Math.round(base * 1.12),
    Math.round(base * 1.08),
    Math.round(base * 1.06),
    Math.round(base * 1.08),
    Math.round(base * 1.10),
    Math.round(base * 1.15),
    Math.round(base * 1.18),
    Math.round(base * 1.19)
  ];
  
  // Promoted forecast (uplift during Ramadan & Summer Surge)
  const promoted = [
    Math.round(base * 0.99),
    Math.round(base * 1.08),
    Math.round(base * 1.28), // Ramadan start boost
    Math.round(base * 1.34),
    Math.round(base * 1.36),
    Math.round(base * 1.32),
    Math.round(base * 1.16),
    Math.round(base * 1.14),
    Math.round(base * 1.17),
    Math.round(base * 1.19),
    Math.round(base * 1.35), // Summer peak
    Math.round(base * 1.42),
    Math.round(base * 1.45)
  ];

  // Bounds
  const upperBound = promoted.map(v => Math.round(v * 1.14));
  const lowerBound = baseline.map(v => Math.round(v * 0.88));

  return {
    labels: TIMEFRAME_WEEKS.map(w => w.label),
    historical: historical,
    baseline: baseline,
    promoted: promoted,
    upperBound: upperBound,
    lowerBound: lowerBound,
    todayIndex: 4, // Feb 9 index
    promos: [
      { name: "Ramadan / Ugadi Surge", startIdx: 6, endIdx: 9, color: "rgba(139, 92, 246, 0.18)" },
      { name: "Summer Heatwave", startIdx: 14, endIdx: 16, color: "rgba(245, 158, 11, 0.18)" }
    ]
  };
}

// Initial Replenishment Suggestions Queue (Grounded in formula: max(0, Target Stock - Physical Stock))
const INITIAL_REPLENISHMENT = [
  {
    id: "REP-2026-001",
    sku_id: "AMUL-FRSH-001",
    product_name: "Amul Taaza Toned Milk (1L Pouch)",
    store_id: "STR-HYD-1021",
    store_name: "Kukatpally KPHB Phase 1 Retail Outlet",
    location: "Kukatpally, Hyderabad",
    channel: "General Trade",
    priority: "critical",
    tag: "Stockout Risk",
    physical_stock: 280,
    target_stock: 1400,
    reorder_qty: 1120, // max(0, 1400 - 280)
    lead_time_days: 1,
    unit_cost: 46.0,
    deadline: "Tomorrow 05:00 AM",
    status: "Pending Review",
    reason: "Morning stockout imminent; inventory buffer dropped below 4 hours of peak sales.",
    decision_log: null
  },
  {
    id: "REP-2026-002",
    sku_id: "AMUL-CHIL-001",
    product_name: "Amul Pasteurised Butter (500g Carton)",
    store_id: "STR-HYD-1011",
    store_name: "Banjara Hills Rd No 12 Exclusive Parlour",
    location: "Banjara Hills, Hyderabad",
    channel: "Amul Parlours",
    priority: "warning",
    tag: "Increase",
    physical_stock: 520,
    target_stock: 1360,
    reorder_qty: 840, // max(0, 1360 - 520)
    lead_time_days: 4,
    unit_cost: 225.0,
    deadline: "May 06, 2026",
    status: "Pending Review",
    reason: "Weekend baking demand velocity projected +28% higher than 4-week baseline.",
    decision_log: null
  },
  {
    id: "REP-2026-003",
    sku_id: "AMUL-AMBI-001",
    product_name: "Amul Pure Cow Ghee (1L Tin)",
    store_id: "STR-HYD-1043",
    store_name: "East Hyderabad Main Milk Depot (Uppal)",
    location: "Uppal, Secunderabad",
    channel: "Distributor / Stockist",
    priority: "optimization",
    tag: "Reduce",
    physical_stock: 4560,
    target_stock: 4000,
    reorder_qty: -560, // Overstock adjustment
    lead_time_days: 6,
    unit_cost: 525.0,
    deadline: "Next Review: May 10",
    status: "Pending Review",
    reason: "Holding 38 days of cover; slow ambient turnaround post-festive peak.",
    decision_log: null
  },
  {
    id: "REP-2026-004",
    sku_id: "AMUL-FRSH-004",
    product_name: "Amul Fresh Malai Paneer (200g Block)",
    store_id: "STR-HYD-1002",
    store_name: "Gachibowli DLF Quick-Hub",
    location: "Gachibowli, Hyderabad",
    channel: "Quick Commerce",
    priority: "critical",
    tag: "Expiry Risk",
    physical_stock: 140,
    target_stock: 460,
    reorder_qty: 320, // max(0, 460 - 140)
    lead_time_days: 2,
    unit_cost: 74.0,
    deadline: "Today 04:00 PM",
    status: "Pending Review",
    reason: "Remaining stock has only 3 days shelf life; execute immediate batch rotation.",
    decision_log: null
  },
  {
    id: "REP-2026-005",
    sku_id: "AMUL-FROZ-001",
    product_name: "Amul Real Ice Cream Vanilla Magic (1L Tub)",
    store_id: "STR-BZA-3001",
    store_name: "Vijayawada Benz Circle Flagship Parlour",
    location: "Benz Circle, Vijayawada",
    channel: "Amul Parlours",
    priority: "warning",
    tag: "Increase",
    physical_stock: 310,
    target_stock: 1250,
    reorder_qty: 940,
    lead_time_days: 5,
    unit_cost: 118.0,
    deadline: "May 08, 2026",
    status: "Pending Review",
    reason: "Coastal summer heatwave temperatures hitting 41°C; ice cream run rate surging.",
    decision_log: null
  },
  {
    id: "REP-2026-006",
    sku_id: "AMUL-AMBI-002",
    product_name: "Amul Kool Kesar Badam (200ml Can)",
    store_id: "STR-VTZ-3015",
    store_name: "RK Beach Promenade Amul Scooping",
    location: "Beach Road, Visakhapatnam",
    channel: "Amul Parlours",
    priority: "warning",
    tag: "Increase",
    physical_stock: 480,
    target_stock: 1800,
    reorder_qty: 1320,
    lead_time_days: 4,
    unit_cost: 26.0,
    deadline: "May 07, 2026",
    status: "Pending Review",
    reason: "High tourist promenade footfall depleting chilled beverage cabinets.",
    decision_log: null
  }
];

// Playbook Section 3.4: Channel Economics Architecture
// Retains team proposed planning mix: GT 50%, MT 17%, Parlours 13%, E-com 8%, Q-Com 7%, HoReCa 5%
const INITIAL_CHANNEL_ECONOMICS = [
  {
    channel: "General Trade (GT)",
    role: "Kirana stores, neighborhood milk booths & daily provisions",
    proposed_allocation: 50.0,
    net_sales_realisation: 100.0,
    product_cost: 76.5,
    channel_distributor_margin: 8.5,
    discounts_promotions: 2.0,
    fulfilment_logistics: 3.5,
    cold_chain_cost: 3.0,
    returns_expiry_wastage: 1.5,
    servicing_cost: 1.0,
    estimated_contribution: 4.0, // 100 - 76.5 - 8.5 - 2 - 3.5 - 3.0 - 1.5 - 1.0
    evidence_status: "Team proposal [PT]",
    key_operating_risk: "Thin per-unit margin on high-frequency fresh pouches; unrecorded stockouts"
  },
  {
    channel: "Modern Trade / Key Accounts",
    role: "Supermarkets and organized retail chains (D-Mart, Ratnadeep, Spencer's)",
    proposed_allocation: 17.0,
    net_sales_realisation: 100.0,
    product_cost: 74.0,
    channel_distributor_margin: 12.0,
    discounts_promotions: 4.5,
    fulfilment_logistics: 2.5,
    cold_chain_cost: 2.0,
    returns_expiry_wastage: 1.2,
    servicing_cost: 1.8,
    estimated_contribution: 2.0,
    evidence_status: "Team proposal [PT]",
    key_operating_risk: "Listing fees, slotted space penalties, and mandatory multi-pack discounts"
  },
  {
    channel: "Amul Parlours / Owned Retail",
    role: "Dedicated brand parlours, scooping booths, COE and railway parlours",
    proposed_allocation: 13.0,
    net_sales_realisation: 100.0,
    product_cost: 72.0,
    channel_distributor_margin: 9.0,
    discounts_promotions: 1.5,
    fulfilment_logistics: 3.0,
    cold_chain_cost: 3.5,
    returns_expiry_wastage: 0.8,
    servicing_cost: 1.2,
    estimated_contribution: 9.0,
    evidence_status: "Team proposal [PT]",
    key_operating_risk: "Deep-freezer capex, electricity uptime, and location rent sensitivity"
  },
  {
    channel: "E-Commerce",
    role: "Scheduled digital grocery deliveries (Amazon Fresh, Flipkart Grocery, BigBasket)",
    proposed_allocation: 8.0,
    net_sales_realisation: 100.0,
    product_cost: 74.0,
    channel_distributor_margin: 11.0,
    discounts_promotions: 4.0,
    fulfilment_logistics: 4.5,
    cold_chain_cost: 2.5,
    returns_expiry_wastage: 1.0,
    servicing_cost: 1.0,
    estimated_contribution: 2.0,
    evidence_status: "Team proposal [PT]",
    key_operating_risk: "Packaging integrity for liquid pouches; platform catalog listing lag"
  },
  {
    channel: "Quick Commerce",
    role: "Urgent top-up & instant 10-15 minute grocery (Blinkit, Instamart, Zepto)",
    proposed_allocation: 7.0,
    net_sales_realisation: 100.0,
    product_cost: 75.0,
    channel_distributor_margin: 13.5,
    discounts_promotions: 3.5,
    fulfilment_logistics: 3.0,
    cold_chain_cost: 2.5,
    returns_expiry_wastage: 1.8,
    servicing_cost: 1.2,
    estimated_contribution: -0.5, // Negative or breakeven warning
    evidence_status: "Team proposal [PT]",
    key_operating_risk: "High platform take-rates can erase margin without disciplined basket sizing"
  },
  {
    channel: "Institutional / HoReCa",
    role: "Hotels, restaurants, bakeries, flight kitchens, hostels & canteens",
    proposed_allocation: 5.0,
    net_sales_realisation: 100.0,
    product_cost: 78.0,
    channel_distributor_margin: 6.0,
    discounts_promotions: 3.0,
    fulfilment_logistics: 2.5,
    cold_chain_cost: 1.5,
    returns_expiry_wastage: 0.5,
    servicing_cost: 1.5,
    estimated_contribution: 7.0,
    evidence_status: "Team proposal [PT]",
    key_operating_risk: "Credit default risk, delayed invoice settlement, and bulk delivery scheduling"
  }
];

// Playbook Section 3.5: City Market Prioritisation Model
// Weights: Demand (25%), Whitespace (25%), Channel Readiness (20%), Cold-Chain (15%), Data Quality (15%)
const INITIAL_MARKET_CITIES = [
  {
    city: "Hyderabad (GHMC + Cyberabad)",
    state: "Telangana",
    tier: "Metro",
    demand_score: 94,
    whitespace_score: 82,
    channel_readiness: 90,
    cold_chain_readiness: 88,
    data_quality_score: 85,
    key_opportunity: "Modern Trade & Quick-Commerce density in Gachibowli, Kondapur, and KPHB.",
    pilot_recommended: true
  },
  {
    city: "Vijayawada & Amaravati",
    state: "Andhra Pradesh",
    tier: "Tier-1 / Hub",
    demand_score: 88,
    whitespace_score: 79,
    channel_readiness: 82,
    cold_chain_readiness: 76,
    data_quality_score: 80,
    key_opportunity: "Commercial hub with strong institutional and transit milk demand at Benz Circle.",
    pilot_recommended: true
  },
  {
    city: "Visakhapatnam (Vizag)",
    state: "Andhra Pradesh",
    tier: "Metro / Port",
    demand_score: 86,
    whitespace_score: 84,
    channel_readiness: 80,
    cold_chain_readiness: 78,
    data_quality_score: 75,
    key_opportunity: "Major ice-cream & beverage summer opportunity along beach tourist belt.",
    pilot_recommended: false
  },
  {
    city: "Warangal (Tri-Cities)",
    state: "Telangana",
    tier: "Tier-2",
    demand_score: 78,
    whitespace_score: 74,
    channel_readiness: 71,
    cold_chain_readiness: 66,
    data_quality_score: 70,
    key_opportunity: "Higher education hub (NIT, KMC) with expanding parlour franchise network.",
    pilot_recommended: false
  },
  {
    city: "Guntur",
    state: "Andhra Pradesh",
    tier: "Tier-2",
    demand_score: 76,
    whitespace_score: 70,
    channel_readiness: 69,
    cold_chain_readiness: 64,
    data_quality_score: 68,
    key_opportunity: "Strong agricultural trade with potential for modern parlour expansion.",
    pilot_recommended: false
  },
  {
    city: "Karimnagar",
    state: "Telangana",
    tier: "Tier-2",
    demand_score: 72,
    whitespace_score: 68,
    channel_readiness: 65,
    cold_chain_readiness: 60,
    data_quality_score: 65,
    key_opportunity: "Northern Telangana gateway; requires route rationalisation from Hyd depot.",
    pilot_recommended: false
  },
  {
    city: "Tirupati",
    state: "Andhra Pradesh",
    tier: "Tier-2 / Pilgrim",
    demand_score: 84,
    whitespace_score: 66,
    channel_readiness: 75,
    cold_chain_readiness: 72,
    data_quality_score: 70,
    key_opportunity: "Massive recurring institutional and pilgrimage dairy volume requirements.",
    pilot_recommended: false
  },
  {
    city: "Rajahmundry",
    state: "Andhra Pradesh",
    tier: "Tier-2",
    demand_score: 70,
    whitespace_score: 62,
    channel_readiness: 62,
    cold_chain_readiness: 58,
    data_quality_score: 62,
    key_opportunity: "Godavari river belt with high fresh dahi & paneer morning consumption.",
    pilot_recommended: false
  }
];

// Central Alerts Register (12 Seeded Live Alerts)
const INITIAL_ALERTS = [
  { id: "ALT-001", severity: "critical", category: "Stockout Alert", title: "Kukatpally Retail Hub Stockout", message: "Amul Taaza Milk 1L stock at 280 units (<4h buffer). Immediate morning refill dispatched.", storeId: "STR-HYD-1021", timestamp: "12 mins ago", status: "Active" },
  { id: "ALT-002", severity: "critical", category: "Cold-Chain Excursion", title: "Freezer Cabinet Thermal Breach (-12°C)", message: "Scooping parlour deep freezer rose from -18°C to -12°C in Banjara Hills. Inspection ticket auto-created.", storeId: "STR-HYD-1011", timestamp: "25 mins ago", status: "Active" },
  { id: "ALT-003", severity: "critical", category: "Stockout Alert", title: "Vijayawada Benz Circle Depot Low Cover", message: "Amul Gold 500ml stockout risk. 410 units on hand vs 2,200 safety threshold.", storeId: "STR-BZA-3002", timestamp: "40 mins ago", status: "Active" },
  { id: "ALT-004", severity: "warning", category: "Expiry Risk", title: "Malai Paneer Batch Expiry (3 Days Left)", message: "140 units of Amul Fresh Malai Paneer at DLF Cyber City quick store approaching expiration date.", storeId: "STR-HYD-1002", timestamp: "1 hour ago", status: "Active" },
  { id: "ALT-005", severity: "warning", category: "Replenishment Delay", title: "DMS Sync Offline > 48 Hours", message: "Nizampet Kirana Point failed to transmit closing inventory data for 2 consecutive cycles.", storeId: "STR-HYD-1029", timestamp: "2 hours ago", status: "Active" },
  { id: "ALT-006", severity: "warning", category: "Forecast Spike", title: "Ramadan Ghee Demand Surge (+42%)", message: "Old City Hyderabad Charminar cluster ordering 42% above normal monthly seasonal baseline.", storeId: "STR-HYD-1051", timestamp: "3 hours ago", status: "Active" },
  { id: "ALT-007", severity: "info", category: "Route Optimization", title: "Secunderabad Morning Route Consolidated", message: "Route 14B re-sequenced to avoid Begumpet metro construction bottlenecks.", storeId: "STR-HYD-1031", timestamp: "4 hours ago", status: "Active" },
  { id: "ALT-008", severity: "warning", category: "Channel Economics", title: "Quick-Commerce Negative Margin Flag", message: "Zepto DLF hub commissions exceeded 14% on small single-pouch orders.", storeId: "STR-HYD-1007", timestamp: "5 hours ago", status: "Active" },
  { id: "ALT-009", severity: "info", category: "Regulatory Update", title: "GST Nil Rate Compliance Check", message: "Verified UHT milk and packaged paneer billed at 0% GST pursuant to 22 Sep 2025 gazette.", storeId: "STR-HYD-1006", timestamp: "6 hours ago", status: "Acknowledged" },
  { id: "ALT-010", severity: "warning", category: "Service Level", title: "Fill Rate Dip in Warangal Depot (91.2%)", message: "Secondary distributor fill rate dropped below 95% target due to highway transit delay.", storeId: "STR-WGL-2003", timestamp: "8 hours ago", status: "Acknowledged" },
  { id: "ALT-011", severity: "info", category: "Pilot Milestone", title: "ARS Pilot Week 4 Audit Completed", message: "Distributor order conversion improved by 14.2% across participating Hyderabad test stores.", storeId: "STR-HYD-1019", timestamp: "12 hours ago", status: "Resolved" },
  { id: "ALT-012", severity: "info", category: "System Sync", title: "GCMMF Anand Master Catalog Reconciled", message: "14 priority SKUs verified against latest price circular circular-2026-Q1.", storeId: "STR-HYD-1001", timestamp: "1 day ago", status: "Resolved" }
];

// Local Storage Helper Utilities for State Persistence
const STORAGE_KEYS = {
  OUTLETS: "amul_outlets_v1",
  REPLENISHMENT: "amul_replenishment_v1",
  ALERTS: "amul_alerts_v1",
  MARKET_WEIGHTS: "amul_market_weights_v1",
  CHANNEL_MIX: "amul_channel_mix_v1",
  FILTER_PREFERENCES: "amul_filters_v1"
};

function getStoredData(key, defaultValue) {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (e) {
    console.warn("localStorage read failed:", e);
    return defaultValue;
  }
}

function setStoredData(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.warn("localStorage write failed:", e);
  }
}

function resetAllDemoData() {
  try {
    Object.values(STORAGE_KEYS).forEach(k => localStorage.removeItem(k));
    location.reload();
  } catch (e) {
    console.error("Reset failed:", e);
  }
}

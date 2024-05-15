// Array of US states
const usStates = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
  ];
  
  // Function to populate the state select dropdown
  function populateStates() {
    const stateSelect = document.getElementById('state-select');
    usStates.forEach(state => {
        const option = document.createElement('option');
        option.value = state;
        option.textContent = state;
        stateSelect.appendChild(option);
    });
  }
  
  // Function to populate the city select dropdown based on the selected state
  function populateCities(state) {
    const citySelect = document.getElementById('city-select');
    // Clear existing options
    citySelect.innerHTML = '';
    // Example: Populate cities based on the selected state (mock data)
    const cities = ["City1", "City2", "City3"]; // Replace with actual cities based on state
    cities.forEach(city => {
        const option = document.createElement('option');
        option.value = city;
        option.textContent = city;
        citySelect.appendChild(option);
    });
  }
  
  // Function to populate the area code select dropdown based on the selected city
  function populateAreaCodes(city) {
    const areaCodeSelect = document.getElementById('area-code-select');
    // Clear existing options
    areaCodeSelect.innerHTML = '';
    // Example: Populate area codes based on the selected city (mock data)
    const areaCodes = ["AreaCode1", "AreaCode2", "AreaCode3"]; // Replace with actual area codes based on city
    areaCodes.forEach(areaCode => {
        const option = document.createElement('option');
        option.value = areaCode;
        option.textContent = areaCode;
        areaCodeSelect.appendChild(option);
    });
  }
  
  // Function to handle change event on state select
  function onStateChange() {
    const stateSelect = document.getElementById('state-select');
    const citySelect = document.getElementById('city-select');
    const areaCodeSelect = document.getElementById('area-code-select');
  
    const selectedState = stateSelect.value;
    if (selectedState === 'random') {
        citySelect.disabled = true;
        areaCodeSelect.disabled = true;
    } else {
        citySelect.disabled = false;
        populateCities(selectedState);
    }
  }
  
  // Function to handle change event on city select
  function onCityChange() {
    const citySelect = document.getElementById('city-select');
    const areaCodeSelect = document.getElementById('area-code-select');
  
    const selectedCity = citySelect.value;
    if (selectedCity === 'random') {
        areaCodeSelect.disabled = true;
    } else {
        areaCodeSelect.disabled = false;
        populateAreaCodes(selectedCity);
    }
  }
  
  // Function to handle click event on generate button
  function onGenerateClick() {
    // Implement generation logic here
  }
  
  // Populate states dropdown on page load
  populateStates();
  
  // Attach event listeners
  document.getElementById('state-select').addEventListener('change', onStateChange);
  document.getElementById('city-select').addEventListener('change', onCityChange);
  document.getElementById('generate-btn').addEventListener('click', onGenerateClick);
  
  
const DOMstrings = {
    stepsBtnClass: 'multisteps-form__progress-btn',
    stepsBtns: document.querySelectorAll('.multisteps-form__progress-btn'),
    stepsBar: document.querySelector('.multisteps-form__progress'),
    stepsForm: document.querySelector('.multisteps-form__form'),
    stepsFormTextareas: document.querySelectorAll('.multisteps-form__textarea'),
    stepFormPanelClass: 'multisteps-form__panel',
    stepFormPanels: document.querySelectorAll('.multisteps-form__panel'),
    stepPrevBtnClass: 'js-btn-prev',
    stepNextBtnClass: 'js-btn-next',
  };
  
  // Remove specific class from all elements in a set
  const removeClasses = (elemSet, className) => {
    elemSet.forEach((elem) => {
      elem.classList.remove(className);
    });
  };
  
  // Find parent element with a specific class
  const findParent = (elem, parentClass) => {
    let currentNode = elem;
    while (currentNode && !currentNode.classList.contains(parentClass)) {
      currentNode = currentNode.parentNode;
      if (!currentNode) return null; // Prevent infinite loop if parent not found
    }
    return currentNode;
  };
  
  // Get the index of the active step button
  const getActiveStep = (elem) => {
    return Array.from(DOMstrings.stepsBtns).indexOf(elem);
  };
  
  // Set the active step button
  const setActiveStep = (activeStepNum) => {
    removeClasses(DOMstrings.stepsBtns, 'js-active');
    DOMstrings.stepsBtns.forEach((elem, index) => {
      if (index <= activeStepNum) {
        elem.classList.add('js-active');
      }
    });
  };
  
  // Get the currently active panel
  const getActivePanel = () => {
    let activePanel = null;
    DOMstrings.stepFormPanels.forEach((elem) => {
      if (elem.classList.contains('js-active')) {
        activePanel = elem;
      }
    });
    return activePanel;
  };
  
  // Set the active panel by index
  const setActivePanel = (activePanelNum) => {
    removeClasses(DOMstrings.stepFormPanels, 'js-active');
    DOMstrings.stepFormPanels.forEach((elem, index) => {
      if (index === activePanelNum) {
        elem.classList.add('js-active');
        setFormHeight(elem);
      }
    });
  };
  
  // Adjust form height to match active panel
  const formHeight = (activePanel) => {
    const activePanelHeight = activePanel.offsetHeight;
    DOMstrings.stepsForm.style.height = `${activePanelHeight}px`;
  };
  
  // Set the form height based on the currently active panel
  const setFormHeight = () => {
    const activePanel = getActivePanel();
    if (activePanel) formHeight(activePanel);
  };
  
  // Click event for step buttons
  DOMstrings.stepsBar.addEventListener('click', (e) => {
    const eventTarget = e.target;
    if (!eventTarget.classList.contains(DOMstrings.stepsBtnClass)) {
      return;
    }
    const activeStep = getActiveStep(eventTarget);
    setActiveStep(activeStep);
    setActivePanel(activeStep);
  });
  
  // Click event for navigation buttons within form panels
  DOMstrings.stepsForm.addEventListener('click', (e) => {
    const eventTarget = e.target;
  
    if (!(eventTarget.classList.contains(DOMstrings.stepPrevBtnClass) ||
          eventTarget.classList.contains(DOMstrings.stepNextBtnClass))) {
      return;
    }
  
    const activePanel = findParent(eventTarget, DOMstrings.stepFormPanelClass);
    let activePanelNum = Array.from(DOMstrings.stepFormPanels).indexOf(activePanel);
  
    if (eventTarget.classList.contains(DOMstrings.stepPrevBtnClass)) {
      activePanelNum--;
    } else {
      activePanelNum++;
    }
  
    setActiveStep(activePanelNum);
    setActivePanel(activePanelNum);
  });
  
  // Set form height on load and resize events
  window.addEventListener('load', setFormHeight, false);
  window.addEventListener('resize', setFormHeight, false);
  
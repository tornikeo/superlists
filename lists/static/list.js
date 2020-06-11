window.Superlists = {};
window.Superlists.initialize = () => {
    // console.log("initialize called");
    $('input[name="text"]').on('keypress', () => {
        // console.log("in keypress handler");
        $('.has-error').hide();
    });
};

// console.log("list.js loaded");

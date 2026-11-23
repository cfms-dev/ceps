// Wrap the tables in CEP bodies in a div, to allow for responsive scrolling

"use strict";

const cepContentId = "cep-content";


// Wrap passed table element in wrapper divs
function wrapTable (table) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("table-wrapper");
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
}


// Wrap all tables in the CEP content in wrapper divs
function wrapCepContentTables () {
    const cepContent = document.getElementById(cepContentId);
    const bodyTables = cepContent.getElementsByTagName("table");
    Array.from(bodyTables).forEach(wrapTable);
}


// Wrap the tables as soon as the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById(cepContentId)) {
        wrapCepContentTables();
    }
})

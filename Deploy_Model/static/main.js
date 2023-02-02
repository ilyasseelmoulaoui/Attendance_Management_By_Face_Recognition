function fermerLaBoite(){
    var element = document.getElementById("boite");
        element.style.display = "none";
}

const to_pres_btn = document.getElementsByClassName("to_present")[0];
const param1 = to_pres_btn.getAttribute("data-param");

to_pres_btn.addEventListener("click", function() {
        var element = document.getElementById("b1");
        element.style.display = "initial";
    return param1;
});

const to_abs_btn = document.getElementsByClassName("to_absent")[0];
const param2 = to_pres_btn.getAttribute("data-param");
to_abs_btn.addEventListener("click", function() {
    var element = document.getElementById("b2");
        element.style.display = "initial";
  return param2;
});

function fermerLaBoiteToPres(){
    var element = document.getElementById("b1");
        element.style.display = "none";
}

function fermerLaBoiteToAbs(){
    var element = document.getElementById("b2");
        element.style.display = "none";
}


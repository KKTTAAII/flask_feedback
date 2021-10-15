let editBtn = document.querySelector("#editBtn")

function myFunction() {
    let form = document.querySelector(".edit_form");
    if (form.style.display === "block") {
      form.style.display = "none";
    } else {
      form.style.display = "block";
      editBtn.style.display = "none";
    }
  }

editBtn.addEventListener("click", function(){
    myFunction();
});
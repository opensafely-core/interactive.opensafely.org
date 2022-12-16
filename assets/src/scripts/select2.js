import $ from "jquery";
import select2 from "select2";
import "select2/dist/css/select2.min.css";
import "@ttskch/select2-bootstrap4-theme/dist/select2-bootstrap4.min.css";

window.$ = window.jQuery = $;
select2($);

$(function () {
  $("#id_users").select2({
    placeholder: "Select 1 or more users to add",
    selectionCssClass: ":all:",
    theme: "bootstrap4",
    width: "100%",
  });
});

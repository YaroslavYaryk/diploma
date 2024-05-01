$(document).ready(function () {
  $(document).on("change", ".btn-file :file", function () {
    var input = $(this),
      label = input.val().replace(/\\/g, "/").replace(/.*\//, "");
    input.trigger("fileselect", [label]);
  });

  $(".btn-file :file").on("fileselect", function (event, label) {
    var input = $(this).parents(".input-group").find(":text"),
      log = label;

    if (input.length) {
      input.val(log);
    } else {
      if (log) alert(log);
    }
  });

  $("#use_zoom").change(function () {
    if ($("#use_zoom").is(":checked")) {
      wheelzoom(document.querySelector("#img_upload"), {
        zoom: 0.1,
        maxZoom: 10,
      });
    } else {
      document
        .querySelector("#img_upload")
        .dispatchEvent(new CustomEvent("wheelzoom.destroy"));
    }
  });

  function cleantables() {
    $("#file_data").children("tr").remove();
    $("#med_data").children("tr").remove();
  }

  function processdata(d) {
    var json = JSON.parse(d);

    for (key in json.generic) {
      $("#file_data").append(
        "<tr><td>" + key + "</td><td>" + json.generic[key] + "</td></tr>"
      );
    }

    for (key in json.med) {
      $("#med_data").append(
        "<tr><td>" + key + "</td><td>" + json.med[key] + "</td></tr>"
      );
    }

    document.getElementById('all_output').style.display = 'none';

    if (json.url != null) {
      document.getElementById('all_output').style.display = 'block';

      $("#img_upload").attr("src", json.url["base64"]);

      $("#img_download").click(function () {
        var a = document.createElement("a"); //Create <a>
        a.href = json.url["base64"]; //Image Base64 Goes here
        a.download = `${json.generic.name.slice(0, -4)}.${json.fileFormat}`; //File name Here
        a.click(); //Downloaded file
      });
    } else {
      $("#img_upload").attr("src", "/static/img/dot.gif");
      $("#modal_dialog").modal("toggle");
    }
  }

  function getBase64(file) {
    var reader = new FileReader();
    reader.readAsDataURL(file);

    let base64;

    reader.onload = function () {
      base64 = reader.result;
      const base64Holder = document.getElementById('image-base64');
      base64Holder.value = base64;
    };
    reader.onerror = function (error) {
      console.log('Error: ', error);
    };

    return base64;
 }

  $("#imgInp").change(function () {
    cleantables();

    var formData = new FormData(document.getElementById("form_one"));

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        processdata(this.responseText);
      }
    };

    getBase64(this.files[0]);
  
    xhr.open("POST", "process.ajax", true);
    xhr.send(formData);
  });
});

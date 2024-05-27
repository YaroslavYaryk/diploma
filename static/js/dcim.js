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

    document.getElementById("all_output").style.display = "none";

    if (json.url != null) {
      document.getElementById("all_output").style.display = "block";

      $("#img_upload").attr("src", json.url["base64"]);

      // Attach download handler
      attachDownloadHandler(json);
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
      const base64Holder = document.getElementById("image-base64");
      const preferrences = document.getElementById("convertation-prefferences");
      base64Holder.value = base64;
      preferrences.value = "HELLO WORLD"
    };
    reader.onerror = function (error) {
      console.log("Error: ", error);
    };


    return base64;
  }

  // Function to attach download click event handler
  function attachDownloadHandler(data) {
    // Unbind any previously attached click event handlers
    $("#img_download").unbind("click");

    // Attach click event handler
    $("#img_download").click(function () {
      var a = document.createElement("a");
      a.href = data.url["base64"];
      a.download = `${data.generic.name.slice(0, -4)}.${data.fileFormat}`;
      a.click();
    });
  }

  $("#imgInp").change(function () {


    const form = document.getElementById("convertation-form");

    form.submit()

    // $("#form_one").find('input:not([type="file"])').val("");
    // cleantables();

    // var formData = new FormData(document.getElementById("form_one"));

    // var xhr = new XMLHttpRequest();

    // xhr.onreadystatechange = function () {
    //   if (this.readyState == 4 && this.status == 200) {
    //     var jsonData = JSON.parse(this.responseText);
    //     processdata(this.responseText);
    //     latestImageData = jsonData; // Store latest image data
    //     attachDownloadHandler(jsonData); // Attach download handler after new image is uploaded
    //   }
    // };
    // getBase64(this.files[0]);

    // xhr.open("POST", "process.ajax", true);
    // xhr.send(formData);
  });
});

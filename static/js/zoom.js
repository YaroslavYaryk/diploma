let globalX = 0;
let globalY = 0;

$(document).on("mousemove", function (e) {
  globalX = e.pageX;
  globalY = e.pageY;
});

$(".table").on("mousemove", function () {
  console.log("aboba");
});

$(".slider_nav__item_big").on("mousemove", function () {
  console.log(34343);
  console.log(globalY);
  let zoom = 5;
  let img = $(".slick-current .full-image").attr("src");
  let imgBlock = $(this).find("img");
  let imgWidth = imgBlock.width();
  let overlay = $(".containerForZoom");
  let cursor = $(".zoom__cursor");
  let maxWidth = $(".slider_nav_big").width();
  cursor.css("width", overlay.width() / zoom + "px");
  cursor.css("height", overlay.height() / zoom + "px");
  let cursorWidth = cursor.outerWidth();
  let cursorHeight = cursor.outerHeight();
  let posX = globalX - $(this).offset().left - cursorWidth / 2;
  let posY = globalY - $(this).offset().top - cursorHeight / 2;

  if (posX < maxWidth / 2 - imgWidth / 2) {
    posX = maxWidth / 2 - imgWidth / 2;
  }
  if (posY < 0) {
    posY = 0;
  }
  if (posX > maxWidth / 2 + imgWidth / 2 - cursorWidth) {
    posX = maxWidth / 2 + imgWidth / 2 - cursorWidth;
  }
  if (posY > $(this).height() - cursorHeight) {
    posY = $(this).height() - cursorHeight;
  }

  cursor.css("left", posX + "px");
  cursor.css("top", posY + "px");
  cursor.show();

  posX -= (maxWidth - imgWidth) / 2;
  posX *= zoom;
  posY *= zoom;

  overlay.css("background-image", `url(${img})`);
  overlay.css("background-size", imgWidth * zoom + "px");
  overlay.css("background-position", `${-posX}px ${-posY}px`);
  overlay.show();
});

$(".slider_nav_big").on("mouseleave", function () {
  $(".zoom__cursor").hide();
  $(".containerForZoom").hide();
});

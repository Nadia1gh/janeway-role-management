    // <!-- popup -->
      document.addEventListener("DOMContentLoaded", function () {
        const searchButtons = document.querySelectorAll(".icon_btn");
        const searchPopup = document.getElementById("searchPopup");
        const closeButton = document.getElementById("searchPopupClose");
        const searchForm = document.getElementById("searchForm");
        const searchInput = document.getElementById("searchInput");
        const searchType = document.getElementById("searchType");



  /* =========================================
     OPEN SEARCH POPUP
  ========================================= */

      searchButtons.forEach(function (searchButton) {
        searchButton.addEventListener("click", function (event) {
          event.preventDefault();

          searchPopup.classList.add("is-open");

          document.body.style.overflow = "hidden";

          if (searchInput) {
            setTimeout(function () {
              searchInput.focus();
            }, 350);
          }
        });
      });

        /* =========================================
     CLOSE POPUP
  ========================================= */

        if (closeButton) {
          closeButton.addEventListener("click", function () {
            closeSearchPopup();
          });
        }

        /* =========================================
     CLICK OUTSIDE
  ========================================= */

        searchPopup.addEventListener("click", function (event) {
          if (event.target === searchPopup) {
            closeSearchPopup();
          }
        });

        /* =========================================
     ESC KEY
  ========================================= */

        document.addEventListener("keydown", function (event) {
          if (event.key === "Escape") {
            closeSearchPopup();
          }
        });

        /* =========================================
   CUSTOM SEARCH SELECT
========================================= */

        const customSelect = document.getElementById("customSearchType");
        const customSelected = customSelect?.querySelector(
          ".custom_select__selected",
        );
        const customOptions = customSelect?.querySelectorAll(
          ".custom_select__option",
        );

        if (customSelect && customSelected && customOptions && searchType) {
          customSelected.addEventListener("click", function () {
            customSelect.classList.toggle("open");
          });

          customOptions.forEach(function (option) {
            option.addEventListener("click", function () {
              const value = this.dataset.value;
              const text = this.textContent.trim();

              // تغییر متن Select
              customSelected.childNodes[0].nodeValue = text + " ";

              // تغییر مقدار Select اصلی
              searchType.value = value;

              // فعال کردن گزینه
              customOptions.forEach(function (item) {
                item.classList.remove("active");
              });

              this.classList.add("active");

              // بستن Dropdown
              customSelect.classList.remove("open");

              // اجرای change برای JavaScript فعلی تو
              searchType.dispatchEvent(new Event("change"));
            });
          });

          // کلیک خارج از Dropdown
          document.addEventListener("click", function (event) {
            if (!customSelect.contains(event.target)) {
              customSelect.classList.remove("open");
            }
          });
        }

        /* =========================================
     SEARCH TYPE CHANGE
  ========================================= */

        if (searchType && searchInput) {
          searchType.addEventListener("change", function () {
            const type = this.value;

            if (type === "author") {
              searchInput.placeholder = "Enter author name...";
            } else if (type === "article") {
              searchInput.placeholder = "Enter article name...";
            } else if (type === "doi") {
              searchInput.placeholder = "Enter DOI...";
            }
          });
        }

        /* =========================================
     SEARCH SUBMIT
  ========================================= */

        if (searchForm) {
          searchForm.addEventListener("submit", function (event) {
            event.preventDefault();

            if (!searchInput || !searchType) {
              return;
            }

            const type = searchType.value;
            const value = searchInput.value.trim();

            if (!value) {
              searchInput.focus();

              return;
            }

            console.log("Search type:", type);
            console.log("Search value:", value);
          });
        }

        /* =========================================
     CLOSE FUNCTION
  ========================================= */

        function closeSearchPopup() {
          searchPopup.classList.remove("is-open");

          document.body.style.overflow = "";
        }
      });

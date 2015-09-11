(function (window, angular, undefined) {

  "use strict";

  var RsvpController = function RsvpController($scope, $log, Restangular) {
    $scope.data = {
      num_attending: 1,
      isFormIncomplete: false,
      isFormInvalid: false
    };

    $scope.submit = function submit() {
      var reservationData = {
        first_name: $scope.data.first_name,
        last_name: $scope.data.last_name,
        address: $scope.data.address,
        email: $scope.data.email,
        num_attending: $scope.data.num_attending
      };

      var isComplete = true;

      _.forEach(reservationData, function (value) {
        isComplete = isComplete && !_.isUndefined(value);
      });

      if (isComplete) {
        $scope.data.isFormIncomplete = false;

        Restangular.all("reservations").post(reservationData)
          .then($scope.onReservationSuccess, $scope.onReservationError);
      }
      else {
        $scope.data.isFormIncomplete = true;
      }
    };

    $scope.onReservationSuccess = function onReservationSuccess(data) {
      $scope.data.reservationId = data.id;
      $scope.data.reservationEmail = data.email;

      //Reservations are full, launch wait list modal...
      if (data.wait_listed == false) {
        $("#wait_list_modal").modal("show");
      }

      //Reservation was successful or user already registered...
      else {
        $("#thank-you-modal").modal("show");
      }
    };

    $scope.onReservationError = function onReservationError(data) {
    };
  };

  RsvpController.$inject = ["$scope", "$log", "Restangular"];

  var thankYouModal = function thankYouModal() {
    return {
      restrict: "E",
      replace: true,
      templateUrl: "/views/thank_you_modal.html"
    };
  };

  var WaitListModalCtrl = function ($scope, Restangular) {
    $scope.onWaitListButtonClick = function onWaitListButtonClick() {
      Restangular.one("reservations", $scope.data.reservationId).post({
        email: $scope.data.reservationEmail
      }).then($scope.onWaitListSuccess, $scope.onWaitListError);
    };

    $scope.onWaitListSuccess = function onWaitListSuccess(data) {
    };

    $scope.onWaitListError = function onWaitListError(data) {
    };
  };

  WaitListModalCtrl.$inject = ["$scope", "Restangular"];

  var waitListModal = function waitListModal() {
    return {
      restrict: "E",
      replace: true,
      controller: WaitListModalCtrl,
      templateUrl: "/views/wait_list_modal.html"
    };
  };

  angular.module("rsvpApp", ["restangular"])
    .config(function (RestangularProvider) {
      RestangularProvider.setBaseUrl("/api/v1/");
      RestangularProvider.setRequestSuffix("/");
      RestangularProvider.setDefaultHttpFields({
        xsrfHeaderName: "X-CSRFToken",
        xsrfCookieName: "csrftoken"
      });
    })
    .controller("RsvpController", RsvpController)
    .directive("thankYouModal", thankYouModal)
    .directive("waitListModal", waitListModal);

})(window, window.angular);
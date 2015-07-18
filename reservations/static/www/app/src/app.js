(function () {

    var RsvpController = function RsvpController($scope, $log, Restangular) {
        $scope.data = {};

        $scope.submit = function submit() {
            var reservationData = {
                first_name: $scope.data.firstName,
                last_name: $scope.data.lastName,
                address: $scope.data.address,
                email: $scope.data.email,
                num_attending: $scope.data.numAttending
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

            //Reservations are full, launch waitlist modal...
            if (data.waitlisted == false) {
                $("#waitlist-modal").modal("show");
            }

            //Reservation was successful or user already registered...
            else {
                $("#thank-you-modal").modal("show");
            }
        };

        $scope.onReservationError = function onReservationError(data) {};
    };

    RsvpController.$inject = ["$scope", "$log", "Restangular"];

    var thankYouModal = function thankYouModal() {
        return {
            restrict: "E",
            replace: true,
            templateUrl: "/reservations/views/thank-you-modal.html"
        };
    };

    var waitlistModalCtrl = function ($scope, Restangular) {
        $scope.onWaitlistButtonClick = function onWaitlistButtonClick() {
            Restangular.one("reservations", $scope.data.reservationId).post({
                email: $scope.data.reservationEmail
            }).then($scope.onWaitlistSuccess, $scope.onWaitlistError);
        };

        $scope.onWaitlistSuccess = function onWaitlistSuccess(data) {};

        $scope.onWaitlistError = function onWaitlistError(data) {};
    };

    waitlistModalCtrl.$inject = ["$scope", "Restangular"];

    var waitlistModal = function waitlistModal() {
        return {
            restrict: "E",
            replace: true,
            controller: waitlistModalCtrl,
            templateUrl: "/reservations/views/waitlist-modal.html"
        };
    };

    angular.module("rsvpApp", ["restangular"])
        .config(function(RestangularProvider) {
            RestangularProvider.setBaseUrl("/reservations/api/");
            RestangularProvider.setDefaultHttpFields({
                xsrfHeaderName: "X-CSRFToken",
                xsrfCookieName: "csrftoken"
            });
        })
        .constant("apiReservationsUrl", "/reservations/api/reservations/")
        .controller("RsvpController", RsvpController)
        .directive("thankYouModal", thankYouModal)
        .directive("waitlistModal", waitlistModal);

}());
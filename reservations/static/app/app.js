(function() {

    var rsvpCtrl = function($scope, $http, $log, apiReservationsUrl) {
        $scope.data = {};

        $scope.submit = function() {
            var reservationData = {
                "first_name": $scope.data.firstName,
                "last_name": $scope.data.lastName,
                "address": $scope.data.address,
                "email": $scope.data.email,
                "num_attending": $scope.data.numAttending
            };

            var isComplete = true;

            angular.forEach(reservationData, function(value, key) {
                isComplete = isComplete && angular.isDefined(value);
            });

            if (isComplete) {
                $scope.data.isFormIncomplete = false;

                $http({
                    method: "POST",
                    url: apiReservationsUrl,
                    data: reservationData,
                    xsrfHeaderName: "X-CSRFToken",
                    xsrfCookieName: "csrftoken"
                }).success($scope.onSuccess).error($scope.onError);

                //$http.post(apiReservationsUrl, reservationData).success(onSuccess).error(onError);
            }
            else {
                $scope.data.isFormIncomplete = true;
            }
        };

        $scope.onSuccess = function(data) {
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

        $scope.onError = function(data) {

        };
    };

    rsvpCtrl.$inject = ["$scope", "$http", "$log", "apiReservationsUrl"];

    var thankYouModal = function() {
        return {
            restrict: "E",
            replace: true,
            templateUrl: "/reservations/views/thank-you-modal.html"
        };
    };

    var waitlistModalCtrl = function($scope, $http, apiReservationsUrl) {
        $scope.onWaitlistButtonClick = function(event) {

        };
    };

    waitlistModalCtrl.$inject = ["$scope", "$http", "apiReservationsUrl"];

    var waitlistModal = function() {
        return {
            restrict: "E",
            replace: true,
            controller: waitlistModalCtrl,
            templateUrl: "/reservations/views/waitlist-modal.html"
        };
    };

    angular.module("rsvpApp", [])
        .constant("apiReservationsUrl", "/reservations/api/reservations/")
        .controller("rsvpCtrl", rsvpCtrl)
        .directive("thankYouModal", thankYouModal)
        .directive("waitlistModal", waitlistModal);

}());
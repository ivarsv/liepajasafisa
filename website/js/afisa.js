var calendar = "oo8r336lk30qjeth0m77gnf9eg@group.calendar.google.com";
var apikey = "AIzaSyAjj0ge6ml5lWYQJSujT7vx26wu5Xfyi0Y";

var afisaApp = angular.module('afisa', ['ngRoute']).config(function($routeProvider, $locationProvider) {
	$locationProvider.hashPrefix('!');
	$routeProvider
		.when('/', { 
			controller: 'AfisaController', 
			templateUrl:'templates/index.html'
		})
		.when('/par', {
			controller: 'ParController', 
			templateUrl: 'templates/about.html'
		})
		.otherwise({
			redirectTo:'/'
		});
});

afisaApp.filter('capitalize', [function(){
	return function(text) {
		return text.charAt(0).toUpperCase() + text.substring(1);
	};
}]);

afisaApp.factory('$calendar', ['dateFilter', function(dateFilter){
	var parseItems = function(items) {
		var result = [];
		angular.forEach(items, function(value) {
			var event = {
				title: value.summary,
				location: value.location,
				description: value.description,
				full: typeof value.start.date != "undefined" 
			};
			
			var date = new Date(Date.parse(value.start.dateTime || value.start.date));
			var utcOffset = date.getTimezoneOffset();
			
			if (event.full) {
				date.setMinutes(date.getMinutes() + utcOffset);
			} else {
				var utcStart = new Date(date.getTime());
				utcStart.setMinutes(utcStart.getMinutes() + utcOffset);
				event.utcStart = utcStart;
				
				var utcEnd = new Date(utcStart.getTime());
				utcEnd.setMinutes(utcEnd.getMinutes() + 90);
				event.utcEnd = utcEnd;
			}
			event.datetime = date;
			result.push(event);
		});
		return result;
	};
	var prepareRequestOptions = function(date) {
		var next = new Date(date.getTime());
		next.setDate(next.getDate() + 1);
		return {
			calendarId: calendar,
			timeMin: dateFilter(date, "yyyy-MM-ddT00:00:00") + "Z",
			timeMax: dateFilter(next, "yyyy-MM-ddT00:00:00") + "Z",
			fields: "items(description,end,location,start,summary)"
		};
	};
	// initialize with API key from API Console
	gapi.client.setApiKey(apikey);
	return function(date, callback) {
		gapi.client.load('calendar', 'v3', function(){
			var request = gapi.client.calendar.events.list(prepareRequestOptions(date));
			request.execute(function(response) {
				callback && callback(parseItems(response.items));
			});
    	});
	};
}]);

afisaApp.controller('AfisaController', ['$scope', '$calendar', function ($scope, $calendar) {
	function dateEventHandler(offset){
		return function() {
			if (!$scope.date || offset == 0) {
				$scope.date = new Date();
			};
			$scope.date.setDate($scope.date.getDate() + offset);
			if (!$scope.loading) {
				$scope.loading = true;
				$calendar($scope.date, function(items) {
					$scope.$apply(function(){
						$scope.loading = false;
						$scope.events = items;
					});
				});
			}
		};
	};
	
	$scope.isViewLoading = false;
	$scope.$on('$routeChangeStart', function() {
	  $scope.isViewLoading = true;
	});
	$scope.$on('$routeChangeSuccess', function() {
	  $scope.isViewLoading = false;
	});
	
	$scope.showall = true;
	
	$scope.handlePrevDay = dateEventHandler(-1);;
	$scope.handleNextDay = dateEventHandler(1);
	$scope.handleDayReset = dateEventHandler(0);
	
	$scope.handleDayReset();
}]);

afisaApp.controller('ParController', ['$scope', function ($scope) {
	FB.XFBML.parse();
	twttr.widgets.load();
}]);

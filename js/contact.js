function hi(input) {
	console.log(input + ': hi');
}

function bye(input) {
	console.log(input + ': bye');
}

var inp = []

class Form {
	constructor() {
		// Initialize everything that needs it
		// Check cache, fill if exists
		//
		hi('constructor');
		this.inputs = {}
		this.min_input_length = 5;
		this.min_name_length = 2;
		this.min_message_length = 6;
		this.max_input_length = 100;
		this.max_message_length = 2000;
		this.previously_validated = false;
		this.editing = true;
		this.xhr_timeout = 10000 // In ms
		this.num_retries = 16;
		this.retry_delay = 500;
		this.check_cache();
		this.get_inputs();
		this.initialize_submit_button();
		this.initialize_inputs();
		// this.request_handler()
		bye('constructor');
	}
	get_inputs() {
		// Gets the input objects and names, return True if works, else False

		let inputs_raw = document.getElementsByClassName('contact-input');
		let filtered = {}
		for (let i = 0; i < inputs_raw.length; i++) {
			let raw = inputs_raw[i];
			if (raw.name != "" && (typeof raw.name) == 'string') {
				filtered[raw.name] = {};
				filtered[raw.name]['object'] = raw;
				filtered[raw.name]['value'] = raw.value;
				// filtered[raw.name]['validating'] = false;
				filtered[raw.name]['valid'] = false;
				filtered[raw.name]['name'] = raw.name;
				filtered[raw.name]['placeholder'] = raw.placeholder;
			}
		}
		this.inputs = filtered;
	}
	initialize_submit_button(option = 'default') {
		// Add event listener to it for relevant functionality

		hi('initialize_submit_button');
		if (option == 'reset') {
			let button = document.getElementById('contact-submit-button');
			button.removeEventListener('click', this.submit_form);
			button.addEventListener('click', this.retry_submit);
			this.update_button('reset');
		}
		else if (option == 'go_home') {
			let button = document.getElementById('contact-submit-button');
			button.removeEventListener('click', this.submit_form);
			button.removeEventListener('click', this.retry_submit);
			button.addEventListener('click', this.go_home_submit);
			this.update_button('go_home');
		}
		else {
			let button = document.getElementById('contact-submit-button');
			button.removeEventListener('click', this.retry_submit);
			button.addEventListener('click', this.submit_form);
			this.update_button('enable');
		}
		bye('initialize_submit_button');
	}
	update_button(value) {
		// Disable button as necessary, ie: when inputs are invalid
		// Updates only when going between all green & not all green
		// Or only when attempting to submit
		// Or continuously after submission attempted but not until then

		hi('update_button');
		let button = document.getElementById('contact-submit-button');
		if (value == 'enable') {
			button.classList.remove('disabled');
			button.classList.remove('reset');
			button.classList.remove('go_home');
			inp.editing = true;
			button.innerHTML = "Send";
		} else if (value == 'disable') {
			button.classList.add('disabled');
			button.classList.remove('reset');
			inp.editing = false;
		} else if (value == 'valid') {
			button.classList.add('valid');
			button.classList.remove('invalid');
			button.classList.remove('reset');
		} else if (value == 'invalid') {
			button.classList.add('invalid');
			button.classList.remove('valid');
			button.classList.remove('reset');
		} else if (value == 'clear') {
			button.classList.remove('invalid');
			button.classList.remove('valid');
			button.classList.remove('reset');
		} else if (value == 'reset') {
			button.classList.remove('invalid');
			button.classList.remove('disabled');
			button.classList.remove('valid');
			button.classList.add('reset');
			button.innerHTML = "Return to Form";
		} else if (value == 'go_home') {
			button.classList.remove('invalid');
			button.classList.remove('disabled');
			button.classList.remove('valid');
			button.classList.add('go_home');
			button.innerHTML = "Return to Home";
		} else {
			console.log('Form > update_button(): invalid option');
			bye('update_button');
			return false;
		}
		bye('update_button');
		return true;

	}
	set_input_states() {
		// Set whether they should be highlighted green/red (valid/invalid)

		hi('set_input_states');
		for (var i = 0; i < Object.keys(this.inputs).length; i++) {
			let input = this.inputs[Object.keys(this.inputs)[i]];
			if (input['valid']) {
				input['object'].classList.add('valid');
				input['object'].classList.remove('invalid');
			} else {
				input['object'].classList.remove('valid');
				input['object'].classList.add('invalid');
			}
		}
		bye('set_input_states');
	}
	validate_inputs() {
		// Check the input values. Automatically change colors of boxes
		// Return T/F
		// Add & remove classes to change the appearance


		hi('validate_inputs');
		this.get_inputs();
		var limit = function(val, type) {
			let types = {
				'email': {
					'min': inp.min_input_length,
					'max': inp.max_input_length
				},
				'name': {
					'min': inp.min_input_length,
					'max': inp.max_input_length
				},
				'message': {
					'min': inp.min_message_length,
					'max': inp.max_message_length
				},
				'else': {
					'min': inp.min_input_length,
					'max': inp.max_input_length
				}
			}
			let min = types[type]['min'];
			let max = types[type]['max'];
			if (val.length >= min && val.length <= max) {
				return true;
			}
			return false;
		}
		let validators = {
			'email': function(value) {
				let mailformat = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
				if (value.match(mailformat) != null) {
					return true;
				}
				return false;
			},
			'name': function(value) {
				if (limit(value, 'name')) {
					return true;
				}
				return false;
			},
			'message': function(value) {
				if (limit(value, 'message')) {
					return true;
				}
				return false;
			},
			'else': function(value) {
				if (limit(value, 'else')) {
					return true;
				}
				return false;
			}
		}
		// Check for validity and update this.inputs metadata
		let has_invalid = false;
		for (var i = 0; i < Object.keys(this.inputs).length; i++) {
			let input = this.inputs[Object.keys(this.inputs)[i]];
			let key = 'else';
			for (var j = 0; j < Object.keys(validators).length; j++) {
				let fnc_name = Object.keys(validators)[j];
				if (fnc_name == input['name']) {
					key = input['name'];
				}
			}
			input['valid'] = validators[key](input['value']); // test the input
			if (!input['valid']) {
				has_invalid = true;
			}
		}
		this.set_input_states();
		this.previously_validated = true;
		if (has_invalid) {
			this.update_button('invalid');
			bye('validate_inputs(f)');
			return false;
		} else {
			this.update_button('valid');
		}
		bye('validate_inputs(t)');
		return true;

	}
	initialize_inputs() {
		// Set up event listeners for the inputs to update and handle changes
		// Don't start validating until after submit is clicked once

		hi('initialize_inputs');
		this.update_button('clear');
		for (var i = 0; i < Object.keys(this.inputs).length; i++) {
			let obj = this.inputs[Object.keys(this.inputs)[i]]['object'];
			obj.addEventListener('input', this.refresh_form);
		}
		bye('initialize_inputs');
	}
	refresh_form() {
		// validate and change colors if necessary
		if (inp.previously_validated && inp.editing) {
			inp.validate_inputs();
		}
	}
	check_cache() {
		// Update values if valid cache exists on wake

	}
	store_cache() {
		// On exit or periodically, store existing values
	}
	retry_submit() {
		inp.update_screen('reset');
		inp.initialize_submit_button();
	}
	go_home_submit(){
		// redirect home
		window.location.replace("/");

	}
	update_screen(func) {
		// Change between the form, sending message, sent message, fail message
		// Sending message has circular arrow or something to show sending
		// Sent message has a green check and a message
		// Fail message has a red 'x'

		hi('update_screen');

		let funcs = {
			'sending': function() {
				inp.update_button('disable');
				for (var i = 0; i < Object.keys(inp.inputs).length; i++) {
					let input = inp.inputs[Object.keys(inp.inputs)[i]]['object'];
					input.classList.add('disabled');
					input.classList.add('noselect');
					input.disabled = true;
				}
				// let form = document.getElementById('contact-form');
				// form.classList.add('hidden');
				let ring = document.getElementsByClassName('profile-main-loader')[0]
				ring.classList.add('visible');
				let ringg = document.getElementsByClassName('circular-loader')[0];
				ringg.classList.add('visible');
				ringg.classList.remove('inactive');
				let contact_status_container = document.getElementById('contact-status-container');
				contact_status_container.classList.add('visible');
				contact_status_container.classList.remove('inactive');
				let mesg = document.getElementById('contact-status-message');
				mesg.innerHTML = 'Sending&nbspMessage';
			},
			'sent': function() {
				let ring = document.getElementsByClassName('loader-path')[0]
				ring.classList.add('pass');
				let ringg = document.getElementsByClassName('circular-loader')[0]
				ringg.classList.add('pass');
				ringg.classList.remove('inactive');
				let ringgg = document.getElementsByClassName('checkmark')[0]
				ringgg.classList.add('pass');
				let mesg = document.getElementById('contact-status-message');
				setTimeout(function () {
					mesg.innerHTML = 'Message&nbspSent'
					mesg.classList.add('pass');
				}, 500);
				let em = document.getElementById('email_input');
				em.style.display = 'none';
				let emm = document.getElementById('message_input');
				em.style.display = 'none';
				let emmm = document.getElementById('name_input');
				em.style.display = 'none';
				setTimeout(function () {
					inp.initialize_submit_button('go_home');
				}, 500);
			},
			'failed': function() {
				let ring = document.getElementsByClassName('loader-path')[0]
				ring.classList.add('fail');
				let ringg = document.getElementsByClassName('circular-loader')[0]
				ringg.classList.add('fail');
				ringg.classList.remove('inactive');
				let ringggg = document.getElementsByClassName('alert-sign')[0]
				ringggg.classList.add('fail');
				let mesg = document.getElementById('contact-status-message');
				setTimeout(function () {
					mesg.innerHTML = 'Message&nbspFailed to&nbspSend';
					mesg.classList.add('fail');
				}, 500);
				let em = document.getElementById('email_input');
				em.style.display = 'none';
				inp.initialize_submit_button('reset');
			},
			'reset': function() {
				inp.update_button('enable');
				let em = document.getElementById('email_input');
				em.style.display = 'block';
				let contact_status_container = document.getElementById('contact-status-container');
				contact_status_container.classList.remove('visible');
				contact_status_container.classList.add('inactive');
				let rng = document.getElementsByClassName('loader-path')[0]
				rng.classList.remove('fail');
				rng.classList.remove('pass');
				let ring = document.getElementsByClassName('profile-main-loader')[0]
				ring.classList.remove('visible');
				let ringg = document.getElementsByClassName('circular-loader')[0]
				ringg.classList.remove('visible');
				ringg.classList.remove('fail');
				ringg.classList.remove('pass');
				ringg.classList.add('inactive');
				let form = document.getElementById('contact-form');
				form.classList.remove('hidden');
				let ringgg = document.getElementsByClassName('checkmark')[0]
				ringgg.classList.remove('pass');
				let ringggg = document.getElementsByClassName('alert-sign')[0]
				ringggg.classList.remove('fail');
				let mesg = document.getElementById('contact-status-message');
				mesg.innerHTML = ''
				mesg.classList.remove('pass');
				mesg.classList.remove('fail');
				for (var i = 0; i < Object.keys(inp.inputs).length; i++) {
					let input = inp.inputs[Object.keys(inp.inputs)[i]]['object'];
					input.classList.remove('disabled');
					input.classList.remove('noselect');
					input.disabled = false;
				}
				inp.editing = true;
			}
		}
		funcs[func]();
		// disable the input areas
		// replace form with an animation or visa versa
		//
		bye('update_screen');
	}
	send_request(passed, failed, tries_left = this.num_retries) {
		// Handles the get request logic
		// Has retries

		hi('send_request');
		console.log(tries_left);
		let url = 'https://l4les7jgafn2cqx5fsojf2oxbq0tvvnr.lambda-url.us-west-2.on.aws'
		const xhr = new XMLHttpRequest();
		xhr.open("POST", url, true);
		xhr.timeout = inp.xhr_timeout;
		var retry_interval = this.retry_delay;
		xhr.setRequestHeader('Content-Type', 'application/json');
		var retry_send_request = function(tries_remaining){
			if (tries_remaining > 0) {
				setTimeout(function () {
					inp.send_request(passed, failed, tries_left = tries_remaining - 1);
				}, retry_interval);
			} else {
				failed();
			}
		}
		xhr.onload = function() {
			if (xhr.status != 200) {
				retry_send_request(tries_left)
			} else {
				passed();
			}
		};
		xhr.onerror = function() {
			if (tries_left > 0) {
				retry_send_request(tries_left)
			} else {
				failed();
			}
		};
		xhr.ontimeout = function(e) {
			if (tries_left > 0) {
				retry_send_request(tries_left)
			} else {
				failed();
			}
		};
		var req_body = {}
		for (var i = 0; i < Object.keys(inp.inputs).length; i++) {
			let input = inp.inputs[Object.keys(inp.inputs)[i]];
			console.log(input);
			let key = input['name'];
			let value = input['value'];
			console.log(key);
			console.log(value);
			req_body[key] = value;
		}
		console.log(req_body);
		// xhr.send(JSON.stringify(
		// 	this.inputs
		// ));
		xhr.send(JSON.stringify(req_body));
		bye('send_request');
	}
	parse_response(raw) {
		hi('parse_response');
		let resp = {
			'success': true
		}
		bye('parse_response');
	}
	submit_form() {
		// Validate, submit request, post updates on sending status
		// Get inputs
		// Validate inputs
		// Change screen to 'sending' state
		// Send request
		// Process response
		// Change screen to result state
		// // If success, just post a success screen
		// // If fail, post a fail screen with option to retry or cancel

		hi('submit_form');
		function passed() {
			hi('passed');
			setTimeout(function () {
				inp.update_screen('sent');
			}, 100);
			bye('passed');
		}
		function failed() {
			hi('failed');
			setTimeout(function () {
				inp.update_screen('failed');
				// setTimeout(function () {
				// 	inp.update_screen('reset');
				// }, 2000);
			}, 100);
			bye('failed');
		}
		let is_editing = inp.editing;
		let inputs_valid = inp.validate_inputs()
		if (is_editing && inputs_valid) {
			inp.update_screen('sending');
			let result = inp.send_request(passed, failed);
			console.log(result);

			// let response = inp.parse_response(inp.send_request());
			// if (response['success']){
			// 	inp.update_screen('sent');
			// }
			// else{
			// 	inp.update_screen('failed');
			// }
		}
		else{
			console.log('button off');
			console.log(is_editing);
			console.log(inputs_valid);
		}
		bye('submit_form');
	}
}

//
// function main() {
// 	var inp = new Form();
// }

// main()

inp = new Form();

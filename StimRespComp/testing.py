from src.haptic_core_serial import *

ports = {'hcc1': 'COM4'}
protocol_version = '1.0'
stop_event = threading.Event()
input_queues = {hcc: Queue() for hcc in ports.keys()}
output_queues = {hcc: Queue() for hcc in ports.keys()}
threads: list[threading.Thread] = []

class Hapticore:
	def stopThreads(self)
		stop_event.set()
		for thread in threads:
			thread.join()

	def application_tick(self, init_angle):
			cur_angle = get_register('report_encoder_angle', output_queues['hcc1'], input_queues['hcc1'])
			diff_to_init = cur_angle - init_angle
			return [cur_angle, diff_to_init]

	def wheel_tracking_fx(self):
		LoG = globals()
		init_angle = get_register('report_encoder_angle', output_queues['hcc1'], input_queues['hcc1'])
		LoG["init_angle"] = init_angle
		while True:
			appl_tick_out = self.application_tick(LoG["init_angle"])
			cur_diff_to_init = appl_tick_out[1]
			if np.absolute(cur_diff_to_init) > 5:
				if cur_diff_to_init < 0:
					if LoG["forward"]==False:
						LoG["fwdBwd_revs"] += 1
					LoG["forward"] = True
				else:
					if LoG["forward"]==True:
						LoG["fwdBwd_revs"] += 1
					LoG["forward"] = False
				init_angle = get_register('report_encoder_angle', output_queues['hcc1'], input_queues['hcc1'])
				LoG["init_angle"] = init_angle
			print()
			print("Number reversals: ", LoG["fwdBwd_revs"])
			if LoG["fwdBwd_revs"] > rev_max:
				LoG["forward"] = np.nan
				LoG["fwdBwd_revs"] = 0
				break
		cur_back_ang = cur_compStim.get("cur_back_ang")
		# H.text_fx(field_name = Reiz, txt = str(cur_back_ang), configureState = True, state = "normal")
		self.button_fx(cur_back_ang = cur_back_ang)
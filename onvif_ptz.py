from utils import translate
import angles

class CameraHasNoPTZProfiles(Exception):
	pass
	
class OnvifPTZ:
		
	def __init__(self, camera, limits):
		self.camera = camera
		self.limits = limits
		
		self.camera.create_media_service()
		profiles = self.camera.media.GetProfiles()
		try:
			self.profile = next(p for p in profiles if 'PTZConfiguration' in p)
		except StopIteration:
			raise CameraHasNoPTZProfiles()
			
		self.camera.create_ptz_service()

	def create_AbsoluteMove(self, pan, tilt, zoom):	
		return {
			'ProfileToken': self.profile.token,
			'Position': self.create_PTZVector(pan, tilt, zoom)
		}

	def create_PTZVector(self, pan, tilt, zoom):
		vec = dict()
		if pan is not None and tilt is not None:
			vec['PanTilt'] = self.create_PanTilt_Vector2D(pan, tilt)
		if zoom is not None:
			vec['Zoom'] = self.create_Zoom_Vector1D(zoom)
		return vec

	def create_PanTilt_Vector2D(self, pan, tilt):
		move_range = self.profile.PTZConfiguration.PanTiltLimits.Range
		x_range = move_range.XRange.Min, move_range.XRange.Max
		y_range = move_range.YRange.Min, move_range.YRange.Max
		
		x = translate(pan, self.limits.az_min, self.limits.az_max, *x_range)
		y = translate(tilt, self.limits.el_min, self.limits.el_max, *y_range)
		
		return {'x': x, 'y': y}

	def create_Zoom_Vector1D(self, zoom):
		zoom_range = self.profile.PTZConfiguration.ZoomLimits.Range
		z_range = zoom_range.XRange.Min, zoom_range.XRange.Max
		
		z = translate(zoom, self.limits.z_min, self.limits.z_max, *z_range)
		return {'x': z}
		
	def move(self, pan, tilt, zoom):
		if tilt is not None:
			tilt = tilt + self.limits.el_off
		if pan is not None:
			pan = pan + self.limits.az_off
			pan, tilt = angles.normalize_sphere(pan, tilt)
			pan = angles.normalize(pan, -180, 180)
		if zoom is not None:
			zoom = zoom + self.limits.z_off
		
		position = self.create_AbsoluteMove(pan, tilt, zoom)
		self.camera.ptz.AbsoluteMove(position)
		
		
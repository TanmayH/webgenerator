from Randomization.WebLayout import WebLayoutProbabilities
from Core.WebGenerator import WebGenerator
from Core.ScreenShutter import ScreenShutter
from Core.DataSetter import DataSetter
from html2image import Html2Image
class Main:
	def run():
		# Set probabilities and settings
		# self,with_sidebar_p, with_header_p, with_navbar_p, with_footer_p, 
    	# layouts_p, boxed_body_p, generate_alert_p, big_header_p, sidebar_first_p, 
		# navbar_first_p, bg_color_classes_p
		layout_p = WebLayoutProbabilities(1,0.6,0.6,None,None,None,None,None,0.8,None,None)
		generator = WebGenerator(layout_p, with_annotations=True, with_color_variation=True)

		# Generate one webpage
		generator.generate_and_save_single()


		# # Set screenshots settings  
		# screen_shutter = ScreenShutter(full_screenshot=True, window_size=(1500,720), driver_path ="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")

		# # Generate multiple webpages and screenshots
		# data_setter = DataSetter(generator, screen_shutter, delete_previous_files=False)
		# data_setter.batch(10)
Main.run()
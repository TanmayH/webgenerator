from dominate.tags import *
from Layout.HtmlComponents import SidebarComponent, HeaderComponent, FooterComponent, NavbarComponent
from Randomization.RandomContent import RandomContent
from Randomization.RandomElements import RandomHtml
from Randomization.RandomHelper import RandomHelper as rh
from Randomization.Elements import ElementsChoices as wcc
from Randomization.WebLayout import WebLayoutProbabilities
import random
import lorem
import json
import os
from Core.FileManager import FileManager as fm
from StyleManager.ColorManager import ColorManager
import copy

class WebGenerator:
	def __init__(self, choices_probabilities=None, with_annotations=False, with_color_variation=False, output_path="./output/"):
		if choices_probabilities is None:
			choices_probabilities = WebLayoutProbabilities(None,None,None,None,None,None,None,None,None,None,None)
		self.choices_probabilities = choices_probabilities
		self.with_annotations = with_annotations
		self.with_color_variation = with_color_variation
		self.output_path = output_path
		self.last_palette = None

	def generate(self, with_annotations=None, with_color_variation=None, output_path=None):
		
		random_website = self.choices_probabilities.weblayout_options_specific()

		with_annotations, with_color_variation, output_path = self.load_defaults_if_none(
			with_annotations=self.with_annotations, 
			with_color_variation=self.with_color_variation, 
			output_path = self.output_path
		)

		#TODO: Refactor, there are a lot of better ways to do the color logic

		#Set defaults
		primary, secondary, light, dark = [(0, 123, 255)], [(108, 117, 125)], [(248, 249, 250)], [(52, 58, 64)] #Bootstrap default color scheme
		enable_gradients = False
		#self.choices_probabilities.bg_color_classes_p = [0,0.5,0.5] #Explicitly set classes probabilities

		border_class = " border" if rh.flip_coin() else ""
		rounded_class = " rounded" if rh.flip_coin() else ""
		shadow_class = " "+self.choices_probabilities.shadow_classes_specific() if rh.flip_coin() else ""

		if with_color_variation: #It only implies css compilation
			primary, secondary, light, dark = ColorManager.random_palette()
			enable_gradients = rh.flip_coin()
			json_dict = { 
				"primary": ColorManager.tuple_to_str(primary),
				"secondary": ColorManager.tuple_to_str(secondary),
				"light": ColorManager.tuple_to_str(light),
				"dark": ColorManager.tuple_to_str(dark),
				"enable-gradients": enable_gradients
			}
			self.last_palette = json_dict
			head = random_website.head
			with head:
				meta(name='wg-palette', content=json.dumps(json_dict))

		color_classes = self.choices_probabilities.color_classes_style_specific()
		component_list = {}

		if "sidebar" in random_website.force_sizes: #TODO: Move options and probabilities 
			bg_class = ColorManager.bg_class_resolver(primary, secondary, light, dark, "sidebar", color_classes, enable_gradients)
			links = RandomContent.links(count_range=(2,6),length_range=(13,13), range_in_chars=True)
			
			sidebar_components = ["sidebar-text" for i in range(len(links))]
			with_heading = rh.flip_coin()
			if (with_heading):
				sidebar_components.insert(0, "sidebar-title")
			
			component_list["sidebar"]=sidebar_components

			random_website.sidebar = SidebarComponent(links, 
			 random_website.force_sizes["sidebar"], 
			 div(lorem.get_word(func="capitalize"),cls="sidebar-heading") if with_heading else "",
			 cls=bg_class+border_class+rounded_class+shadow_class, data_wg_type = "sidebar"
			)
		if "header" in random_website.force_sizes:
			bg_class = ColorManager.bg_class_resolver(primary, secondary, light, dark, "header", color_classes, enable_gradients)

			random_website._header = HeaderComponent(RandomContent.title((2,8)), 
			 random_website.force_sizes["header"], HeaderComponent.Mode.Heading, data_wg_type = "header",
			  cls=bg_class+border_class+rounded_class+shadow_class,
			)
			component_list["header"]=["header-title"]
		if "navbar" in random_website.force_sizes:
			bg_class = ColorManager.bg_class_resolver(primary, secondary, light, dark, "navbar", color_classes, enable_gradients)

			navbar_align_options = [NavbarComponent.Align.Center, NavbarComponent.Align.Left, NavbarComponent.Align.Right]
			navbar_align = random.choice(navbar_align_options)

			links = RandomContent.links(count_range=(2,6),length_range=(13,13), range_in_chars=True)
			with_heading =  rh.flip_coin()
			navbar_components = ["navbar-text" for i in range(len(links))]
			if (with_heading):
				navbar_components.insert(0, "navbar-title")
			navbar_components.insert(0, navbar_align)

			random_website.navbar = NavbarComponent(links,
			 random_website.force_sizes["navbar"], navbar_align,
			  a(lorem.get_word(func="capitalize"),cls="navbar-brand", href="#") if with_heading else "",
			  cls=bg_class+border_class+rounded_class+shadow_class,  data_wg_type = "navbar"
			 )
			component_list["navbar"]= navbar_components
		if "footer" in random_website.force_sizes:
			bg_class = ColorManager.bg_class_resolver(primary, secondary, light, dark, "footer", color_classes, enable_gradients)

			random_website._footer = FooterComponent(RandomContent.credits((50,50), True), 
			 random_website.force_sizes["footer"], FooterComponent.Mode.Credits, cls=bg_class+border_class+rounded_class+shadow_class,
			  data_wg_type = "footer"
			 )
			component_list["footer"]=["footer-title"]

		random_website.build()
		if ({"sidebar":[]} in random_website.layout_list and component_list.get("sidebar",-1)!=-1):
			index = random_website.layout_list.index({"sidebar":[]})
			random_website.layout_list[index]["sidebar"] = component_list["sidebar"]
		if ({"header":[]} in random_website.layout_list and component_list.get("header",-1)!=-1):
			index=random_website.layout_list.index({"header":[]})
			random_website.layout_list[index]["header"] = component_list["header"]
		if ({"navbar":[]} in random_website.layout_list and component_list.get("navbar",-1)!=-1):
			index=random_website.layout_list.index({"navbar":[]})
			random_website.layout_list[index]["navbar"] = component_list["navbar"]
		if ({"footer":[]} in random_website.layout_list and component_list.get("footer",-1)!=-1):
			index=random_website.layout_list.index({"footer":[]})
			random_website.layout_list[index]["footer"] = component_list["footer"]

		#Color classes for wrapper and body
		_body = random_website.get(tag="body")[0]
		body_bg_class = ColorManager.bg_class_resolver(primary, secondary, light, dark, "body", color_classes, enable_gradients)

		if "class" in _body.attributes:
			_body.attributes["class"] = _body.attributes["class"]+" "+body_bg_class
		else:
			_body.attributes["class"] = body_bg_class

		wrapper = random_website.get(id="full-wrapper")[0]
		wrapper_bg_class = ColorManager.bg_class_resolver(primary, secondary, light, dark, "wrapper", color_classes, enable_gradients)

		if "class" in wrapper.attributes:
			wrapper.attributes["class"] = wrapper.attributes["class"]+" "+wrapper_bg_class
		else:
			wrapper.attributes["class"] = wrapper_bg_class

		content = random_website.get(id="page-content")[0]

		#ADD content part 
		content_components = []
		with content:
			page_type = wcc.page_type_specific()
			if page_type == wcc.PageTypes.Content:
				RandomHtml.sections(wcc.n_sections_specific(), content_components, with_annotations)
				if ({"content":[]} in random_website.layout_list and content_components != []):
					index = random_website.layout_list.index({"content":[]})
					random_website.layout_list[index]["content-section"] = content_components
					del random_website.layout_list[index]["content"]
			elif page_type == wcc.PageTypes.Form:
				RandomHtml.form(wcc.n_form_rows_specific(), content_components)
				if ({"content":[]} in random_website.layout_list and content_components != []):
					index = random_website.layout_list.index({"content":[]})
					random_website.layout_list[index]["content-form"] = content_components
					del random_website.layout_list[index]["content"]
			else:
				raise Exception("Not implemented for page type {0}".format(page_type))

		final_content_list = []
		for pair in random_website.layout_list:
			key = list(pair.keys())[0]
			if (pair[key] != []):
				final_content_list.append(pair)
		random_website.layout_list = final_content_list

		return random_website
	
	def write_to_gui_file(self, layout_list):
		pass

	def generate_and_save_single(self, output_path=None, delete_previous_files=True, with_annotations=False, with_color_variation=True):
		if output_path is None:
			output_path = self.output_path

		fm.prepare_output(output_path, delete_previous_files, with_annotations)

		website = self.generate(with_annotations, with_color_variation, output_path)
		for i in website.layout_list:
			print(i)
		# print(website.layout_list)
		orig_website = copy.deepcopy(website)
		orig_website.head[-1]="" 

		if with_color_variation and self.last_palette is not None:
			palette = self.last_palette
			ColorManager.compile_color(primary=palette["primary"], secondary=palette["secondary"], light=palette["light"], 
				 dark=palette["dark"], enable_gradients=palette["enable-gradients"])

		html_output = os.path.join(output_path, "html")
		fm.save(os.path.join(html_output,"random_webpage.html"), orig_website.render())
		fm.save(os.path.join(html_output,"random_webpage_sketch.html"), website.render())
		print("Generated random_webpage.html in "+html_output)

		self.write_to_gui_file(website.layout_list)
		
	def create_if_not_exists(self, path): #TODO: Unify calls to files between generator and DataSetter
		if not os.path.exists(path):
			os.mkdir(path)

	def load_defaults_if_none(self,**kwargs):
		for key, value in kwargs.items():
			if value is not None:
				yield value
			else:
				yield getattr(self,key)


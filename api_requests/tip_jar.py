from api.web import APIHandler
from api.web import PrettyPrintAPIMixin
from api.server import handle_api_url
from api.server import handle_api_html_url

from libs import db

@handle_api_url("tip_jar")
class TipJarContents(APIHandler):
	return_name = "tip_jar"
	allow_get = True
	login_required = False
	pagination = True
	sid_required = False
	auth_required = False

	def post(self):
		self.append(self.return_name,
					db.c.fetch_all(
						"SELECT donation_id AS id, donation_amount AS amount, donation_message AS message, "
							"CASE WHEN donation_private IS TRUE THEN 'Anonymous' ELSE username END AS name "
						"FROM r4_donations LEFT JOIN phpbb_users USING (user_id) "
						"ORDER BY donation_id DESC " + self.get_sql_limit_string()
					)
		)

@handle_api_html_url("tip_jar")
class TipJarHTML(PrettyPrintAPIMixin, TipJarContents):
	login_required = False
	auth_required = False

	def get(self):
		self.write(self.render_string("basic_header.html", title=self.locale.translate("tip_jar")))
		self.write("<p>%s</p>" % self.locale.translate("tip_jar_opener"))
		self.write("<ul><li>%s</li>" % self.locale.translate("tip_jar_instruction_1"))
		self.write("<li>%s</li>" % self.locale.translate("tip_jar_instruction_2"))
		self.write("<li>%s</li></ul>" % self.locale.translate("tip_jar_instruction_3"))
		self.write("<p>%s</p>" % self.locale.translate("tip_jar_opener_end"))

		self.write("""
			<div style='text-align: center'>
			<form method="post" action="https://www.paypal.com/cgi-bin/webscr" target="paypal">
			<input type="hidden" name="cmd" value="_xclick">
			<input type="hidden" name="business" value="rmcauley@gmail.com">
			<input type="hidden" name="item_name" value="">
			<input type="hidden" name="bn"  value="ButtonFactory.PayPal.001">
			<input type="image" name="add" src="/static/images4/paypal.gif">
			</form>
			</div>""")

		all_donations = db.c.fetch_var("SELECT SUM(donation_amount) FROM r4_donations WHERE user_id != 2 AND donation_amount > 0")
		self.write("<p>%s: %s</p>" % (self.locale.translate("tip_jar_all_donations"), all_donations))

		balance = db.c.fetch_var("SELECT SUM(donation_amount) FROM r4_donations")
		self.write("<p>%s: %s</p>" % (self.locale.translate("tip_jar_balance"), balance))

		super(TipJarHTML, self).get(write_header=False)

	def sort_keys(self, keys):
		return [ 'name', 'amount', 'message' ]
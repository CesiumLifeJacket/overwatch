$(document).ready(function ()
{
	var jsonStr = $("#output").text();
	var jsonObj = $.parseJSON(jsonStr);
	var newel = $("#new");
	var code = $("#code").text().split("\n");
	$.each(jsonObj, function()
	{
		newel.append("<ul>");
		$.each($(this), function()
		{
			newel.append("<li>Message:"+this.message+"</li>");
			newel.append("<li>Error Type:"+this["type"]+"</li>");
			newel.append("<li>Row:"+this.row+"</li>");
			newel.append("<li>Col:"+this.col+"</li>");
			code[this.row - 1] = code[this.row - 1].substring(0, this.col - 1) + "<span class=\"error "+this["type"]+"\" title=\""+this.message+"\">" + code[this.row - 1].substring(this.col - 1) + "</span>";
		});
		newel.append("</ul>");
	});
	$("#code").text("");
	$("#code").append("<pre>");
	$.each(code, function()
	{
		$("#code").append(this + "\n");
	});
	$("#code").append("</pre>");
});